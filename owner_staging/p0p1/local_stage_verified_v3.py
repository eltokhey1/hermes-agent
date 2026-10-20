"""V3: verify and consume the EXACT same bounded ZIP bytes (no source TOCTOU).

Offline stage-only, not runtime authorization. Refuses linked path ancestors and
requires a trusted, locally controlled destination parent; no Windows integration.
"""
from __future__ import annotations
import argparse
import io
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path,PurePosixPath

WINDOWS_RESERVED={"CON","PRN","AUX","NUL",*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10))}
MAX_TOTAL=50*1024*1024
MAX_FILE=10*1024*1024
MAX_COUNT=250
MAX_ZIP_BYTES=80*1024*1024

def _is_link(path:Path)->bool:
    return path.is_symlink() or bool(getattr(path,"is_junction",lambda:False)())

def _require_unlinked_ancestors(path:Path)->None:
    """Refuse symlinks/junctions on every visible ancestor (no TOCTOU guarantee)."""
    for item in (path, *path.parents):
        if _is_link(item):
            raise ValueError("linked source or destination path refused")

def _tracked_porcelain_count(payload:bytes)->int:
    """Count changed TRACKED paths in porcelain v1 -z, consuming rename extra field."""
    if not isinstance(payload,bytes) or not payload.endswith(b"\0") and payload:
        raise ValueError("malformed Git status data")
    if not payload:
        return 0
    parts=payload.split(b"\0")
    i=0
    count=0
    while i < len(parts)-1:
        entry=parts[i]
        if len(entry)<4 or entry[2:3]!=b" " or any(code not in b" MADRCUT?!" for code in entry[:2]):
            raise ValueError("unrecognized Git porcelain status")
        status=entry[:2]
        if status in (b"??",b"!!"):
            raise ValueError("unexpected untracked status")
        if any(code in b"RC" for code in status):
            i+=1
            if i>=len(parts)-1 or not parts[i]:
                raise ValueError("missing rename/copy source")
        count+=1
        i+=1
    return count

def hash_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def _safe_name(name:str)->Path:
    if '\\' in name or '\x00' in name or name.startswith('/') or not name or ':' in name or any(ord(c)<32 for c in name):
        raise ValueError('unsafe ZIP name')
    if any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('noncanonical ZIP components')
    p=PurePosixPath(name)
    if any(x in ('..','.') for x in p.parts) or not p.parts:
        raise ValueError('unsafe ZIP traversal')
    for component in p.parts:
        if component.rstrip(' .') != component or component.split('.')[0].rstrip(' ').upper() in WINDOWS_RESERVED or component.split('.')[0].upper() in {'CONIN$', 'CONOUT$', 'COM¹', 'COM²', 'COM³', 'LPT¹', 'LPT²', 'LPT³'}:
            raise ValueError('unsafe Windows component')
    return Path(*p.parts)

def stage_archive(zip_path:Path, expected_sha256:str, target:Path)->dict:
    zip_path=Path(zip_path).expanduser().absolute()
    target=Path(target).expanduser().absolute()
    _require_unlinked_ancestors(zip_path)
    _require_unlinked_ancestors(target)
    if not re.fullmatch('[a-fA-F0-9]{64}',expected_sha256):
        raise ValueError('required external SHA256 pin')
    # Read only once from a single open descriptor: hash and unzip those exact
    # bytes, not a potentially changed file reopened after digest verification.
    # Memory bounded to <= 80 MiB plus a small read buffer. Do not follow
    # directory aliases and do not use this as a hostile filesystem sandbox.
    with zip_path.open('rb') as source:
        archive_bytes = source.read(MAX_ZIP_BYTES + 1)
    if len(archive_bytes) > MAX_ZIP_BYTES:
        raise ValueError("ZIP file larger than bounded staging limit")
    actual = hashlib.sha256(archive_bytes).hexdigest()
    if actual.lower() != expected_sha256.lower():
        raise ValueError('SHA256 mismatch, refusing import')
    if target.exists() or _is_link(target):
        raise FileExistsError('stage target must be NEW; never overwrite')
    parent=target.parent
    if not parent.is_dir():
        raise FileNotFoundError('create parent explicitly first')
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        members=z.infolist()
        if not members or len(members)>MAX_COUNT:raise ValueError('invalid file count')
        seen=set()
        component_casing={}
        file_paths=set()
        directory_paths=set()
        size=0
        for info in members:
            rel=_safe_name(info.filename.rstrip('/'))
            if info.is_dir() and info.filename != rel.as_posix()+'/':
                raise ValueError("noncanonical ZIP directory name")
            if str(rel).casefold() == 'staging_receipt.json':
                raise ValueError('reserved stage marker')
            key=str(rel).casefold()
            for j in range(1,len(rel.parts)+1):
                prefix='/'.join(rel.parts[:j]); normalized=prefix.casefold()
                if normalized in component_casing and component_casing[normalized]!=prefix:
                    raise ValueError('Windows parent-case collision')
                component_casing[normalized]=prefix
            if key in seen:raise ValueError('casefold collision')
            seen.add(key)
            if info.is_dir():directory_paths.add(key)
            else:file_paths.add(key)
            ftype=(info.external_attr>>16)&0o170000
            if ftype==stat.S_IFLNK or ftype not in (0,stat.S_IFDIR,stat.S_IFREG):
                raise ValueError('unexpected ZIP member type')
            if info.file_size>MAX_FILE:raise ValueError('file too large')
            size+=info.file_size
            if size>MAX_TOTAL:raise ValueError('archive too large')
        for file_path in file_paths:
            if file_path in directory_paths or any('/'.join(file_path.split('/')[:j]) in file_paths for j in range(1,len(file_path.split('/')))):
                raise ValueError('ZIP file/directory prefix conflict')
        # Use a temporary sibling to prevent partially staged contents on failure.
        scratch=Path(tempfile.mkdtemp(prefix='.hermes-import-',dir=parent))
        try:
            for info in members:
                rel=_safe_name(info.filename.rstrip('/'))
                dest=scratch/rel
                if info.is_dir():
                    dest.mkdir(parents=True,exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    digest=hashlib.sha256()
                    copied=0
                    with z.open(info) as src,dest.open('xb') as dst:
                        while True:
                            chunk=src.read(1024*1024)
                            if not chunk:break
                            copied+=len(chunk)
                            if copied>info.file_size or copied>MAX_FILE:
                                raise ValueError('ZIP member exceeded declared size')
                            dst.write(chunk);digest.update(chunk)
                    if copied!=info.file_size or hash_file(dest)!=digest.hexdigest():
                        raise ValueError('post-copy hash inconsistency')
            # Marker is descriptive; it cannot attest host readiness.
            (scratch/'STAGING_RECEIPT.json').write_text(json.dumps({"source_zip_sha256":actual,"staged_files":sum(not i.is_dir() for i in members),"host_verified":False,"production":"HOLD","operation":"stage_only_no_execution"},indent=2)+'\n',encoding='utf8')
            scratch.rename(target)
        finally:
            if scratch.exists():shutil.rmtree(scratch)
    return {"target":str(target),"files":sum(not i.is_dir() for i in members),"sha256":actual,"gate":"NO-GO"}

def host_snapshot(repo:Path)->dict:
    """Read only; report no filenames, command-lines, credentials, home paths or secret values."""
    out={"os":platform.system(),"python":platform.python_version(),"git_available":bool(shutil.which('git')),"docker_on_path":bool(shutil.which('docker')),"host_verified":False,"production":"HOLD"}
    if not out['git_available'] or not repo.is_dir() or _is_link(repo):return out
    try:
        safe_env=os.environ.copy()
        safe_env['GIT_OPTIONAL_LOCKS']='0'
        rev=subprocess.run(['git','-c','core.fsmonitor=false','--no-optional-locks','rev-parse','--verify','HEAD'],cwd=repo,capture_output=True,text=True,timeout=8,env=safe_env)
        dirty=subprocess.run(['git','-c','core.fsmonitor=false','--no-optional-locks','status','--porcelain=v1','-z','--untracked-files=no'],cwd=repo,capture_output=True,timeout=8,env=safe_env)
        if rev.returncode==0 and dirty.returncode==0:
            out['git_head']=rev.stdout.strip()
            out['tracked_dirty_count']=_tracked_porcelain_count(dirty.stdout)
            out['repo_git_read_ok']=True
    except (OSError,subprocess.TimeoutExpired,ValueError):out['repo_git_read_ok']=False
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('stage');s.add_argument('--archive',required=True);s.add_argument('--sha256',required=True);s.add_argument('--target',required=True)
    h=sub.add_parser('host-snapshot');h.add_argument('--repo',required=True)
    a=p.parse_args()
    v=stage_archive(Path(a.archive),a.sha256,Path(a.target)) if a.command=='stage' else host_snapshot(Path(a.repo))
    print(json.dumps(v,ensure_ascii=False,indent=2))

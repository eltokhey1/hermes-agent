"""Stage an explicitly downloaded, SHA-256-pinned archive to a NEW directory; never touch Hermes installation."""
from __future__ import annotations
import argparse
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

def hash_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def _safe_name(name:str)->Path:
    if '\\' in name or '\x00' in name or name.startswith('/') or not name or ':' in name:
        raise ValueError('unsafe ZIP name')
    if any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('noncanonical ZIP components')
    p=PurePosixPath(name)
    if any(x in ('..','.') for x in p.parts) or not p.parts:
        raise ValueError('unsafe ZIP traversal')
    for component in p.parts:
        if component.rstrip(' .') != component or component.split('.')[0].rstrip(' ').upper() in WINDOWS_RESERVED:
            raise ValueError('unsafe Windows component')
    return Path(*p.parts)

def stage_archive(zip_path:Path, expected_sha256:str, target:Path)->dict:
    zip_path=Path(zip_path).resolve()
    target=Path(target).expanduser().resolve()
    if not re.fullmatch('[a-fA-F0-9]{64}',expected_sha256):
        raise ValueError('required external SHA256 pin')
    actual=hash_file(zip_path)
    if actual.lower()!=expected_sha256.lower():
        raise ValueError('SHA256 mismatch, refusing import')
    if target.exists():
        raise FileExistsError('stage target must be NEW; never overwrite')
    parent=target.parent
    if not parent.is_dir():
        raise FileNotFoundError('create parent explicitly first')
    with zipfile.ZipFile(zip_path) as z:
        members=z.infolist()
        if not members or len(members)>MAX_COUNT:raise ValueError('invalid file count')
        seen=set()
        component_casing={}
        file_paths=set()
        directory_paths=set()
        size=0
        for info in members:
            rel=_safe_name(info.filename.rstrip('/'))
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
    if not out['git_available'] or not repo.is_dir():return out
    try:
        rev=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=repo,capture_output=True,text=True,timeout=8)
        dirty=subprocess.run(['git','status','--porcelain','-z','--untracked-files=no'],cwd=repo,capture_output=True,timeout=8)
        if rev.returncode==0 and dirty.returncode==0:
            out['git_head']=rev.stdout.strip()
            out['tracked_dirty_count']=len([x for x in dirty.stdout.split(b'\x00') if x])
            out['repo_git_read_ok']=True
    except (OSError,subprocess.TimeoutExpired):out['repo_git_read_ok']=False
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('stage');s.add_argument('--archive',required=True);s.add_argument('--sha256',required=True);s.add_argument('--target',required=True)
    h=sub.add_parser('host-snapshot');h.add_argument('--repo',required=True)
    a=p.parse_args()
    v=stage_archive(Path(a.archive),a.sha256,Path(a.target)) if a.command=='stage' else host_snapshot(Path(a.repo))
    print(json.dumps(v,ensure_ascii=False,indent=2))

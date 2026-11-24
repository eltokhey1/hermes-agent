"""Hermes HX P1: RESEARCH-ONLY local OS broker + synthetic owner + same-host witness.

No real browser/MCP/inline effect is executed; dispatch produces inert previews only.
NOT an offhost witness, not human login, not a security acceptance of Hermes.
"""
from __future__ import annotations
import base64
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import secrets
import socket
import socketserver
import struct
import subprocess
import sys
import tempfile
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ALLOWED = frozenset(("browser.navigate", "mcp.invoke", "inline.memory"))
BLOCKED = "NO-GO"


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def digest(x):
    return hashlib.sha256(canon(x)).hexdigest()

def b64(x):
    return base64.urlsafe_b64encode(x).decode().rstrip("=")

def unb64(x):
    if not isinstance(x, str) or len(x)>8192:
        raise ValueError("invalid_encoding")
    return base64.urlsafe_b64decode(x + "=" * (-len(x)%4))

def verify(pub, payload, signature):
    try:
        pub.verify(unb64(signature), canon(payload))
        return True
    except Exception:
        return False

def call(sock_path, req):
    s=socket.socket(socket.AF_UNIX)
    s.settimeout(6)
    s.connect(str(sock_path))
    with s:
        s.sendall(canon(req)+b"\n")
        line=b""
        while not line.endswith(b"\n"):
            x=s.recv(8192)
            if not x:raise RuntimeError("broken_ipc")
            line+=x
            if len(line)>20000:raise RuntimeError("oversized_reply")
        return json.loads(line)

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            peer_uid=struct.unpack("3i",self.request.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[1]
            line=self.rfile.readline(12000)
            req=json.loads(line)
            if not isinstance(req,dict):raise ValueError("invalid_request")
            reply=self.server.act(peer_uid,req)
        except Exception as e:
            reply={"ok":False,"code":str(e)[:120]}
        self.wfile.write(canon(reply)+b"\n")

class Server(socketserver.UnixStreamServer):
    allow_reuse_address=True

class Witness:
    def __init__(self,owner_pub, signing_key, log_file):
        self.owner_pub=Ed25519PublicKey.from_public_bytes(owner_pub)
        self.key=Ed25519PrivateKey.from_private_bytes(signing_key)
        self.log_file=Path(log_file)
        self.count=0
        self.root="0"*64
        self.nonces=set()
    def act(self,uid,req):
        if uid!=0 or set(req)!={"op","grant","signature","event"} or req["op"]!="append":
            raise ValueError("WITNESS_OWNER_PROCESS_ONLY")
        grant=req["grant"]
        if not isinstance(grant,dict) or not verify(self.owner_pub,grant,req["signature"]):
            raise ValueError("WITNESS_FORGED_APPROVAL")
        event=req["event"]
        if set(event)!={"action","task_id","sha","args_sha256","nonce","result"} or event["result"]!="SYNTHETIC_PREVIEW_ONLY":
            raise ValueError("WITNESS_INVALID_EVENT")
        if any(grant.get(k)!=event[k] for k in ("action","task_id","sha","args_sha256","nonce")) or grant.get("action") not in ALLOWED:
            raise ValueError("WITNESS_MISMATCH")
        if event["nonce"] in self.nonces:raise ValueError("WITNESS_REPLAY")
        self.count+=1
        packet={"sequence":self.count,"previous":self.root,"event_sha256":digest(event),"source_sha":event["sha"],"environment":"research-same-host","PRODUCTION":"HOLD"}
        signature=b64(self.key.sign(canon(packet)))
        receipt={"payload":packet,"signature":signature}
        self.root=digest(receipt)
        self.nonces.add(event["nonce"])
        with self.log_file.open("a") as f:
            f.write(json.dumps(receipt,sort_keys=True)+"\n")
            f.flush();os.fsync(f.fileno())
        return {"ok":True,"receipt":receipt}

class Broker:
    def __init__(self,owner_key, owner_pub, witness_path, hermes_home, expected_sha, worker_uid):
        self.key=Ed25519PrivateKey.from_private_bytes(owner_key)
        self.pub=Ed25519PublicKey.from_public_bytes(owner_pub)
        self.witness_path=witness_path
        self.home=Path(hermes_home)
        self.expected_sha=expected_sha
        self.worker_uid=worker_uid
        self.used=set()
        self.epoch=1
    def act(self,uid,req):
        op=req.get("op")
        if op=="approve":
            if uid!=0:raise ValueError("OWNER_IDENTITY_NOT_AUTHENTICATED")
            if set(req)!={"op","action","task_id","sha","args_sha256","ttl"}:
                raise ValueError("BAD_OWNER_APPROVAL_FIELDS")
            if req["action"] not in ALLOWED or req["sha"]!=self.expected_sha or type(req["ttl"]) is not int or not 1<=req["ttl"]<=60:
                raise ValueError("OWNER_SCOPE_DENIED")
            if not all(isinstance(req[k],str) and len(req[k])==n and all(c in '0123456789abcdef' for c in req[k]) for k,n in (("task_id",32),("sha",40),("args_sha256",64))):
                raise ValueError("INVALID_OWNER_HASH")
            grant={k:req[k] for k in ("action","task_id","sha","args_sha256")}
            grant.update({"nonce":secrets.token_hex(16),"epoch":self.epoch,"expires":int(time.time())+req["ttl"],"audience":"hermes-hx-p1-synthetic-broker"})
            return {"ok":True,"grant":grant,"signature":b64(self.key.sign(canon(grant)))}
        if op in ("estop","resume"):
            if uid!=0:raise ValueError("OWNER_IDENTITY_NOT_AUTHENTICATED")
            if set(req)!={"op"}:raise ValueError("BAD_ESTOP_FIELDS")
            if op=="estop":
                (self.home/"ESTOP").write_text(json.dumps({"reason":"synthetic-owner-estop","engaged_at":"test"})+"\n")
                (self.home/"ESTOP").chmod(0o600)
            else:
                (self.home/"ESTOP").unlink(missing_ok=True)
                self.epoch+=1
            return {"ok":True,"state":op,"epoch":self.epoch}
        if op=="dispatch":
            if uid!=self.worker_uid:raise ValueError("WORKER_UID_MISMATCH")
            if set(req)!={"op","action","task_id","sha","args","grant","signature"}:
                raise ValueError("BAD_WORKER_FIELDS")
            g=req["grant"]
            if not isinstance(g,dict) or set(g)!={"action","task_id","sha","args_sha256","nonce","epoch","expires","audience"}:
                raise ValueError("MALFORMED_GRANT")
            if not verify(self.pub,g,req["signature"]):raise ValueError("INVALID_SIGNATURE")
            if (self.home/"ESTOP").exists():raise ValueError("ESTOP_ENGAGED")
            if g["epoch"]!=self.epoch:raise ValueError("STALE_EPOCH")
            if type(g["expires"]) is not int or int(time.time())>=g["expires"]:raise ValueError("EXPIRED_GRANT")
            if g["nonce"] in self.used:raise ValueError("REPLAY")
            if g["audience"]!="hermes-hx-p1-synthetic-broker" or g["action"] not in ALLOWED:
                raise ValueError("INVALID_AUDIENCE_OR_ACTION")
            for k in ("action","task_id","sha"):
                if req[k]!=g[k]:raise ValueError("SCOPE_MISMATCH")
            if req["sha"]!=self.expected_sha or digest(req["args"])!=g["args_sha256"]:
                raise ValueError("SOURCE_OR_ARGUMENT_MISMATCH")
            self.used.add(g["nonce"])
            event={k:g[k] for k in ("action","task_id","sha","args_sha256","nonce")}
            event["result"]="SYNTHETIC_PREVIEW_ONLY"
            try: w=call(self.witness_path,{"op":"append","grant":g,"signature":req["signature"],"event":event})
            except Exception as e:raise ValueError("WITNESS_UNAVAILABLE") from e
            if not w.get("ok"):raise ValueError("WITNESS_REJECTED")
            return {"ok":True,"result":"SYNTHETIC_PREVIEW_ONLY","receipt":w["receipt"],"release":"NO-GO"}
        raise ValueError("OPERATION_DENIED")

def serve(path, instance, mode, ready):
    sp=Path(path)
    sp.unlink(missing_ok=True)
    srv=Server(str(sp),Handler)
    srv.act=instance.act
    os.chmod(sp,mode)
    ready.put("ready")
    try:srv.serve_forever(poll_interval=.05)
    finally:srv.server_close();sp.unlink(missing_ok=True)

def worker_mode():
    cfg=json.loads(Path(sys.argv[2]).read_text())
    broker=cfg['broker'];phase=cfg['phase'];source=cfg['source_sha']; pub=Ed25519PublicKey.from_public_bytes(unb64(cfg['witness_pub']))
    def send(action,args,record):
        return call(broker,{"op":"dispatch","action":action,"task_id":record['grant']['task_id'],"sha":source,"args":args,"grant":record['grant'],"signature":record['signature']})
    def require(condition,msg):
        if not condition:raise AssertionError(msg)
    assert os.getuid()!=0
    proc=Path('/proc/self/status').read_text()
    assert 'CapEff:\t0000000000000000' in proc and 'CapBnd:\t0000000000000000' in proc and 'NoNewPrivs:\t1' in proc
    sentinel=Path(os.environ['HERMES_HOME'])/'ESTOP'
    if phase=='normal':
        assert not sentinel.exists()
        for action,args,record in cfg['plans']:
            ok=send(action,args,record)
            require(ok.get('ok') is True,'valid signed grant should be accepted')
            require(ok.get('result')=='SYNTHETIC_PREVIEW_ONLY','real effects must stay impossible')
            require(ok['release']=='NO-GO','must remain HOLD')
            require(verify(pub,ok['receipt']['payload'],ok['receipt']['signature']),'independent witness signature invalid')
            again=send(action,args,record)
            require(again.get('ok') is False and again['code']=='REPLAY','replay not denied')
        a,args,rec=cfg['plans'][0]
        forged={**rec,'signature':b64(b'\0'*64)}
        require(not send(a,args,forged)['ok'],'forged signature accepted')
        require(not send('mcp.invoke',args,rec)['ok'],'cross-effect replay accepted')
        require(not send(a,{"different":True},rec)['ok'],'argument substitution accepted')
        require(not call(broker,{"op":"approve","action":a,"task_id":rec['grant']['task_id'],"sha":source,"args_sha256":digest(args),"ttl":10})['ok'],'agent faked owner')
        print('HX_P1_UNIFIED_SYNTHETIC_NORMAL=PASS 3/3 previewed signed effects + signatures + replay/cross-effect/arguments/owner checks',flush=True)
    elif phase=='estop':
        if os.environ.get("HX_LOCAL_SKIP_SOURCE")=="1":
            assert sentinel.exists(),"local preflight only"
        else:
            from agent import estop
            assert estop.is_engaged() is True
        a,args,rec=cfg['plans'][0]
        denied=send(a,args,rec)
        require(denied.get('code')=='ESTOP_ENGAGED','ESTOP did not fail-close new work')
        require(not call(broker,{"op":"resume"})['ok'],'unprivileged agent cleared ESTOP')
        try:sentinel.unlink()
        except OSError:pass
        else:raise AssertionError('agent cleared root-owned ESTOP')
        print('HX_P1_ESTOP=PASS '+('synthetic local sentinel preflight' if os.environ.get('HX_LOCAL_SKIP_SOURCE')=='1' else 'real Hermes agent.estop.is_engaged')+' + broker denial + protected sentinel',flush=True)
    elif phase=='resume':
        if os.environ.get("HX_LOCAL_SKIP_SOURCE")=="1":
            assert not sentinel.exists(),"local preflight only"
        else:
            from agent import estop
            assert estop.is_engaged() is False
        a,args,rec=cfg['plans'][0]
        result=send(a,args,rec)
        require(result.get('ok') is True,'new epoch valid grant not accepted')
        print('HX_P1_RESUME=PASS new owner decision/new epoch permitted synthetic preview',flush=True)
    elif phase=='stale':
        a,args,rec=cfg['plans'][0]
        require(send(a,args,rec).get('code')=='STALE_EPOCH','old epoch grant accepted')
        print('HX_P1_STALE_EPOCH=PASS',flush=True)
    else:raise RuntimeError('unknown mode')


def main():
    assert os.geteuid()==0,'hosted harness MUST be root after namespace setup'
    source=os.environ.get('HX_SOURCE_SHA','a'*40)
    assert len(source)==40
    uid=int(os.environ.get('HX_RUNNER_UID','65534'))
    gid=int(os.environ.get('HX_RUNNER_GID','65534'))
    assert uid!=0
    python=os.environ.get('HERMES_PYTHON',sys.executable)
    with tempfile.TemporaryDirectory(prefix='hx-p1-gate-') as td:
        base=Path(td);base.chmod(0o755)
        home=base/'owner-home';home.mkdir(mode=0o711);os.chmod(home,0o711)
        broker_path=str(base/'broker.sock');witness_path=str(base/'witness.sock')
        audit=base/'witness.jsonl';audit.touch(mode=0o600)
        owner_priv=Ed25519PrivateKey.generate();witness_priv=Ed25519PrivateKey.generate()
        raw=lambda k:k.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
        pub=lambda k:k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        ctx=mp.get_context('fork')
        q1,q2=ctx.Queue(),ctx.Queue()
        w=ctx.Process(target=serve,args=(witness_path,Witness(pub(owner_priv),raw(witness_priv),audit),0o600,q1),daemon=True)
        b=ctx.Process(target=serve,args=(broker_path,Broker(raw(owner_priv),pub(owner_priv),witness_path,home,source,uid),0o666,q2),daemon=True)
        w.start();assert q1.get(timeout=5)=='ready'
        b.start();assert q2.get(timeout=5)=='ready'
        def grant(action,args):
            req={"op":"approve","action":action,"task_id":secrets.token_hex(16),"sha":source,"args_sha256":digest(args),"ttl":30}
            r=call(broker_path,req)
            assert r['ok'],r
            return r
        def run_phase(phase,plans):
            packet={"phase":phase,"broker":broker_path,"source_sha":source,"plans":plans,"witness_pub":b64(pub(witness_priv))}
            file=base/f'{phase}.json';file.write_text(json.dumps(packet));file.chmod(0o644)
            cmd=['setpriv',f'--reuid={uid}',f'--regid={gid}','--clear-groups','--no-new-privs','--bounding-set=-all','--inh-caps=-all','--ambient-caps=-all',python,'-B',str(Path(__file__).resolve()),'worker',str(file)]
            env={**os.environ,'HERMES_HOME':str(home),'PYTHONPATH':os.environ.get('GITHUB_WORKSPACE',str(Path(__file__).resolve().parent)),'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
            r=subprocess.run(cmd,text=True,capture_output=True,env=env,timeout=35)
            print(r.stdout.strip(),flush=True)
            if r.returncode!=0:raise RuntimeError(f'worker {phase} failed {r.returncode}: {r.stderr[-1100:]}')
            return r
        try:
            a=[('browser.navigate',{'url':'https://example.invalid/fixture'}),('mcp.invoke',{'server':'synthetic-only','tool':'inert.preview'}),('inline.memory',{'action':'preview','value':'synthetic'})]
            p=[(k,v,grant(k,v)) for k,v in a]
            run_phase('normal',p)
            before_stop=[(a[0][0],a[0][1],grant(*a[0]))]
            assert call(broker_path,{'op':'estop'})['ok']
            run_phase('estop',before_stop)
            assert call(broker_path,{'op':'resume'})['ok']
            run_phase('stale',before_stop)
            run_phase('resume',[(a[0][0],a[0][1],grant(*a[0]))])
            lines=audit.read_text().strip().splitlines()
            assert len(lines)==4,f'expected witness 4 receipts, got {len(lines)}'
            root='0'*64
            for i,line in enumerate(lines,1):
                receipt=json.loads(line); payload=receipt['payload']
                assert payload['previous']==root and payload['sequence']==i and verify(witness_priv.public_key(),payload,receipt['signature'])
                root=digest(receipt)
            print('HX_P1_SAME_HOST_WITNESS=PASS 4/4 Ed25519 receipts, monotonic sequence and hash-chain',flush=True)
            print('HX_P1_PRODUCTION=HOLD HITL=REQUIRED REAL_BROWSER_MCP_INLINE_E2E=NOT_ATTESTED OFFHOST_WITNESS=NOT_ATTESTED HUMAN_OWNER_AUTH=NOT_ATTESTED',flush=True)
        finally:
            b.terminate();w.terminate();b.join(3);w.join(3)
            if b.is_alive():b.kill()
            if w.is_alive():w.kill()

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker_mode()
    else:main()

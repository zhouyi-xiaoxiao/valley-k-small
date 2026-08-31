#!/usr/bin/env python3
"""Per-job/task H9 runtime: verified TMPDIR execution and atomic output export."""
from __future__ import annotations

import argparse, hashlib, json, os, re, shutil, stat, subprocess, tempfile
from pathlib import Path

H7_SHA="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
H8_SHA="bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H9_MANIFEST="notes/isambard_ai_v4_r2_h9_payload.sha256"
H8_MANIFEST="notes/isambard_ai_v4_r2_h8_payload.sha256"
OLD_ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"
HEX=re.compile(r"[0-9a-f]{64}")
SAFE_ABS=re.compile(r"/[A-Za-z0-9._/-]+")

def req(x: bool, msg: str)->None:
    if not x: raise ValueError(msg)

def sha_bytes(data: bytes)->str: return hashlib.sha256(data).hexdigest()
def sha(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def safe_name(name: str)->Path:
    p=Path(name); req(not p.is_absolute() and ".." not in p.parts and p.as_posix()==name and name not in ("","."),"unsafe relative path"); return p

def parse_manifest(root: Path, anchor: str, *, file_mode:int, dir_mode:int)->list[tuple[str,str]]:
    req(HEX.fullmatch(anchor) is not None,"invalid external H9 anchor")
    root=root.absolute(); st=root.lstat(); req(stat.S_ISDIR(st.st_mode) and not root.is_symlink() and stat.S_IMODE(st.st_mode)==dir_mode,"unsafe root")
    m=root/H9_MANIFEST; req(m.is_file() and not m.is_symlink() and sha(m)==anchor,"H9 pinned manifest drift")
    raw=m.read_bytes(); req(raw.endswith(b"\n") and b"\r" not in raw,"manifest canonical bytes")
    rows=[]
    for line in raw.decode().splitlines():
        z=re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)",line); req(z is not None,"manifest row syntax")
        d,n=z.groups(); safe_name(n); rows.append((d,n))
    req(len(rows)==len({n for _,n in rows}),"duplicate manifest member")
    expected={n for _,n in rows}|{H9_MANIFEST}; actual=set()
    for cur,dirs,files in os.walk(root,followlinks=False):
        for name in dirs:
            p=Path(cur)/name; s=p.lstat(); req(stat.S_ISDIR(s.st_mode) and not p.is_symlink() and stat.S_IMODE(s.st_mode)==dir_mode,"unsafe directory inventory")
        for name in files:
            p=Path(cur)/name; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==file_mode,"unsafe file inventory")
            actual.add(p.relative_to(root).as_posix())
    req(actual==expected,"closed inventory drift")
    for d,n in rows: req(sha(root/n)==d,f"member drift: {n}")
    req(sha(root/H8_MANIFEST)==H8_SHA and sha(root/"notes/isambard_ai_v4_r2_h7_payload.sha256")==H7_SHA,"fixed H8/H7 parent drift")
    return rows

def safe_ancestors(path: Path, stop: Path)->None:
    q=path
    while True:
        if q.exists() or q.is_symlink(): req(not q.is_symlink(),"ancestor symlink")
        if q==stop: break
        req(q!=q.parent,"ancestor escape"); q=q.parent

def trusted_absolute(path:Path, *, must_exist:bool)->Path:
    absolute=path.absolute(); req(SAFE_ABS.fullmatch(str(absolute)) is not None,"unsafe absolute path quoting")
    if must_exist: req(absolute.exists(),"root missing")
    probe=absolute if absolute.exists() else absolute.parent
    while True:
        req(not probe.is_symlink(),"ancestor symlink")
        if probe==probe.parent: break
        probe=probe.parent
    return absolute

def copy_package(package:Path,snapshot:Path,h9:str)->dict[str,str]:
    rows=parse_manifest(package,h9,file_mode=0o600,dir_mode=0o700)
    req(not snapshot.exists() and not snapshot.is_symlink(),"snapshot collision")
    snapshot.mkdir(parents=False,mode=0o700)
    baseline={}
    for digest,name in (*rows,(h9,H9_MANIFEST)):
        target=snapshot/safe_name(name); target.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(package/name,target); os.chmod(target,0o400); baseline[name]=digest
    for cur,dirs,_ in os.walk(snapshot): os.chmod(cur,0o700)
    parse_manifest(snapshot,h9,file_mode=0o400,dir_mode=0o700)
    parse_manifest(package,h9,file_mode=0o600,dir_mode=0o700)
    return baseline

def load_inputs(run:Path,snapshot:Path,records:list[dict],baseline:dict[str,str])->dict[str,str]:
    result={}
    for record in records:
        req(set(record)=={"path","sha256"} and HEX.fullmatch(record["sha256"]) is not None,"phase-input schema")
        name=record["path"]; safe_name(name); req(name.startswith("artifacts/"),"phase input outside artifacts")
        req(name not in baseline and name not in result,"phase input collision")
        source=run/name; safe_ancestors(source,run); st=source.lstat(); req(stat.S_ISREG(st.st_mode) and not source.is_symlink() and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600,"unsafe phase input")
        req(sha(source)==record["sha256"],"phase input digest drift")
        target=snapshot/name; target.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(source,target); os.chmod(target,0o400); result[name]=record["sha256"]
    return result

def snapshot_args(args:list[str],run:Path,package:Path,snapshot:Path,imported:dict[str,str])->list[str]:
    result=[]
    for value in args:
        if value.startswith(str(run)+"/"):
            name=Path(value).relative_to(run).as_posix(); req(name in imported,"argv run path lacks bound phase input"); result.append(str(snapshot/name))
        else:
            req(not value.startswith(str(package)+"/") and not value.startswith("/"),"argv absolute path bypasses snapshot")
            result.append(value)
    return result

def inventory(root:Path)->dict[str,dict]:
    out={}
    for cur,dirs,files in os.walk(root,followlinks=False):
        for d in dirs:
            p=Path(cur)/d; s=p.lstat(); req(stat.S_ISDIR(s.st_mode) and not p.is_symlink() and stat.S_IMODE(s.st_mode)==0o700,"runtime directory drift")
        for f in files:
            p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode) in (0o400,0o600),"runtime file drift")
            out[p.relative_to(root).as_posix()]={"sha256":sha(p),"mode":stat.S_IMODE(s.st_mode)}
    return out

def execute(config:dict)->dict:
    required={"schema","phase","package_root","run_root","h9","h8","h7","science_path","science_sha256","science_bytes_hex","phase_args","phase_inputs"}
    req(set(config)==required and config["schema"]=="h9-runtime-config-v1","runtime config schema")
    req(config["h8"]==H8_SHA and config["h7"]==H7_SHA and HEX.fullmatch(config["h9"]) is not None,"runtime parent anchors")
    submitted=os.environ.get("H9_SUBMITTED_SCRIPT_SHA256",""); req(HEX.fullmatch(submitted) is not None,"submitted-script binding")
    job=os.environ.get("SLURM_JOB_ID",""); array=os.environ.get("SLURM_ARRAY_JOB_ID",""); task=os.environ.get("SLURM_ARRAY_TASK_ID","")
    req(job and (job.isdecimal() or re.fullmatch(r"[0-9]+_[0-9]+",job) is not None),"SLURM job identity")
    if config["phase"]=="production": req(array.isdecimal() and task.isdecimal() and 0<=int(task)<480,"production array identity")
    else: req(task=="" and array=="","unexpected array identity")
    raw_tmp=os.environ.get("SLURM_TMPDIR",""); req(raw_tmp.startswith("/"),"SLURM_TMPDIR missing/nonabsolute")
    package=trusted_absolute(Path(config["package_root"]),must_exist=True); run=trusted_absolute(Path(config["run_root"]),must_exist=True); tmp=trusted_absolute(Path(raw_tmp),must_exist=True)
    req(str(tmp) not in ("","/") and tmp.is_dir(),"SLURM_TMPDIR unsafe")
    req(package!=run and package not in run.parents and run not in package.parents,"roots mixed")
    suffix=f"{array}_{task}" if task else job; snapshot=tmp/f"h9-{config['phase']}-{suffix}"; baseline=copy_package(package,snapshot,config["h9"])
    imported=load_inputs(run,snapshot,config["phase_inputs"],baseline); before={**baseline,**imported}
    science=bytes.fromhex(config["science_bytes_hex"]); req(sha_bytes(science)==config["science_sha256"],"captured science bytes drift")
    req(config["science_path"] in baseline and baseline[config["science_path"]]==config["science_sha256"],"science manifest binding")
    text=science.decode(); req(OLD_ROOT in text,"frozen science root missing")
    body="\n".join(x for x in text.splitlines()[1:] if not x.startswith("#SBATCH")).replace(OLD_ROOT,str(snapshot))+"\n"
    derived=body.encode(); derived_sha=sha_bytes(derived)
    effective_args=snapshot_args(config["phase_args"],run,package,snapshot,imported)
    env=os.environ.copy(); env.update({"H9_PACKAGE_ROOT":str(package),"H9_RUN_ROOT":str(run),"H9_SNAPSHOT_ROOT":str(snapshot),"H9_PAYLOAD_SHA256":config["h9"],"H8_PAYLOAD_SHA256":H8_SHA,"H7_PAYLOAD_SHA256":H7_SHA})
    completed=subprocess.run(["bash","-s","--",*effective_args],input=derived,cwd=snapshot,env=env,check=False)
    req(completed.returncode==0,"science body failed")
    after=inventory(snapshot)
    for name,digest in before.items(): req(name in after and after[name]["sha256"]==digest and after[name]["mode"]==0o400,"pre/post immutable input drift")
    new=sorted(set(after)-set(before)); req(all(n.startswith("artifacts/") for n in new),"output outside artifacts")
    outputs=[]
    for name in new:
        source=snapshot/name; target=run/name; safe_ancestors(target.parent,run); target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        req(not target.exists() and not target.is_symlink(),"output collision")
        fd,tempname=tempfile.mkstemp(prefix=".h9-output.",dir=target.parent); os.close(fd); temp=Path(tempname)
        try:
            shutil.copyfile(source,temp); os.chmod(temp,0o600); req(sha(temp)==after[name]["sha256"],"output copy drift"); os.link(temp,target)
        finally: temp.unlink(missing_ok=True)
        outputs.append({"path":name,"sha256":after[name]["sha256"]})
    parse_manifest(package,config["h9"],file_mode=0o600,dir_mode=0o700)
    receipt={"schema":"h9-runtime-receipt-v1","status":"PASS_H9_RUNTIME_EXECUTED_FROM_JOB_PRIVATE_SNAPSHOT","phase":config["phase"],"h9":config["h9"],"h8":H8_SHA,"h7":H7_SHA,"package_root":str(package),"run_root":str(run),"snapshot_root":str(snapshot),"slurm_job_id":job,"slurm_array_job_id":array or None,"slurm_array_task_id":int(task) if task else None,"submitted_script_sha256":submitted,"science_source":{"path":config["science_path"],"sha256":config["science_sha256"],"derived_body_sha256":derived_sha},"phase_args_sha256":sha_bytes(json.dumps(config["phase_args"],separators=(",",":"),ensure_ascii=True).encode()),"effective_phase_args_sha256":sha_bytes(json.dumps(effective_args,separators=(",",":"),ensure_ascii=True).encode()),"phase_inputs":config["phase_inputs"],"outputs":outputs,"terminal_sacct_identity":{"job_id":job,"array_job_id":array or None,"array_task_id":int(task) if task else None}}
    receipts=run/"artifacts/h9_receipts"; receipts.mkdir(parents=True,exist_ok=True,mode=0o700)
    name=f"{config['phase']}-{array}_{task}.json" if task else f"{config['phase']}-{job}.json"; target=receipts/name; req(not target.exists(),"runtime receipt collision")
    target.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n"); os.chmod(target,0o600)
    return receipt

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--config",type=Path,required=True); a=p.parse_args(); config=json.loads(a.config.read_text()); print(json.dumps(execute(config),sort_keys=True)); return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except (ValueError,OSError,json.JSONDecodeError) as e: print(f"FAIL-CLOSED: {e}",file=os.sys.stderr); raise SystemExit(2)

#!/usr/bin/env python3
"""H8 content-bound, split-root Slurm submission boundary (fail closed)."""
from __future__ import annotations

import hashlib, json, os, re, shlex, shutil, stat, subprocess, tempfile
from pathlib import Path

H7_SHA = "7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
H8_MANIFEST = "notes/isambard_ai_v4_r2_h8_payload.sha256"
HEX = re.compile(r"[0-9a-f]{64}")
PHASES = ("v3_authority", "canary", "production", "reducer", "replay", "combined", "release", "terminal")
SCRIPTS = {
 "v3_authority":"isambard_ai_gating_v4_r2_v3_authority_h4.sbatch",
 "canary":"isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
 "production":"isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
 "reducer":"isambard_ai_gating_v4_r2_reduce_h4.sbatch",
 "replay":"isambard_ai_gating_v4_r2_replay_h4.sbatch",
 "combined":"isambard_ai_gating_v4_r2_combined_h4.sbatch",
 "release":"isambard_ai_gating_v4_r2_release_h5.sbatch",
 "terminal":"isambard_ai_gating_v4_r2_terminal_h8.sbatch",
}
OLD_ROOT = "/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"

def req(x: bool, msg: str) -> None:
    if not x: raise ValueError(msg)

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def rows(root: Path, anchor: str) -> list[tuple[str,str]]:
    req(HEX.fullmatch(anchor) is not None, "missing/forged H8 anchor")
    m=root/H8_MANIFEST; req(m.is_file() and not m.is_symlink() and sha(m)==anchor,"H8 external anchor drift")
    out=[]
    for line in m.read_text().splitlines():
        z=re.fullmatch(r"([0-9a-f]{64})  ([^\x00\r\n]+)",line); req(z is not None,"manifest syntax")
        d,n=z.groups(); q=Path(n); req(not q.is_absolute() and ".." not in q.parts and q.as_posix()==n,"manifest traversal")
        out.append((d,n))
    req(len(out)==len(set(n for _,n in out)),"duplicate member")
    return out

def verify_package(root: Path, h8: str, h7: str=H7_SHA, *, file_mode: int=0o600, dir_mode: int=0o700) -> dict:
    root=root.absolute(); st=root.lstat(); req(stat.S_ISDIR(st.st_mode) and not root.is_symlink() and stat.S_IMODE(st.st_mode)==dir_mode,"package root unsafe")
    rr=rows(root,h8); expected={n for _,n in rr}|{H8_MANIFEST}; actual=set()
    for cur,ds,fs in os.walk(root,followlinks=False):
        for d in ds:
            p=Path(cur)/d; req(p.is_dir() and not p.is_symlink() and stat.S_IMODE(p.lstat().st_mode)==dir_mode,"ancestor symlink or directory mode")
        for f in fs:
            p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==file_mode,"unsafe package member")
            actual.add(p.relative_to(root).as_posix())
    req(actual==expected,"closed-world inventory drift")
    for d,n in rr: req(sha(root/n)==d,"package member drift")
    req(sha(root/"notes/isambard_ai_v4_r2_h7_payload.sha256")==h7==H7_SHA,"H7 fixed anchor drift")
    return {"h8":h8,"h7":h7,"members":len(rr)}

def safe_roots(package: Path, run: Path) -> tuple[Path,Path]:
    p=package.absolute(); r=run.absolute(); req(p!=r and p not in r.parents and r not in p.parents,"roots mixed")
    for leaf in (p,r.parent):
        for q in (leaf,*leaf.parents): req(q.exists() and not q.is_symlink(),"root ancestor unsafe")
    if r.exists(): req(r.is_dir() and not r.is_symlink(),"run root unsafe")
    return p,r

def make_snapshot(package: Path, run: Path, phase: str, h8: str) -> Path:
    req(phase in PHASES,"unknown phase"); snap=run/"private_snapshots"/phase
    req(not snap.exists(),"stage snapshot already exists")
    snap.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    shutil.copytree(package,snap,copy_function=shutil.copyfile)
    for cur,ds,fs in os.walk(snap):
        os.chmod(cur,0o500)
        for f in fs: os.chmod(Path(cur)/f,0o400)
    verify_package(snap,h8,file_mode=0o400,dir_mode=0o500)
    return snap

def seed_or_verify_run(package: Path, run: Path, h8: str) -> None:
    """Create/verify the writable execution copy without trusting its imports."""
    rr=rows(package,h8)
    for digest,name in rr:
        source=package/name; target=run/name
        cursor=target.parent
        while cursor != run.parent:
            req(not cursor.is_symlink(),"run seed ancestor symlink")
            if cursor == run: break
            cursor=cursor.parent
        if not target.exists():
            req(not target.is_symlink(),"run seed symlink")
            target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            shutil.copyfile(source,target); os.chmod(target,0o600)
        req(target.is_file() and not target.is_symlink() and sha(target)==digest,"run source mutation")
    manifest=run/H8_MANIFEST
    if not manifest.exists():
        manifest.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(package/H8_MANIFEST,manifest); os.chmod(manifest,0o600)
    req(sha(manifest)==h8,"run manifest mutation")
    (run/"logs").mkdir(mode=0o700,exist_ok=True)

def receipt_path(run: Path, phase: str, job: str) -> Path: return run/"h8_receipts"/f"{phase}-{job}.json"

def validate_receipt(path: Path, phase: str, h8: str, h7: str, package: Path, run: Path) -> dict:
    req(path.is_file() and not path.is_symlink(),"missing runtime receipt downstream")
    st=path.lstat(); req(st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600,"forged runtime receipt")
    v=json.loads(path.read_text()); req(v=={"phase":phase,"h8":h8,"h7":h7,"package_root":str(package),"run_root":str(run),"status":"PASS_H8_RUNTIME_PRE_POST"},"forged runtime receipt")
    return v

def render(package: Path, run: Path, snapshot: Path, phase: str, h8: str, h7: str, args: list[str]) -> bytes:
    src=package/"code"/SCRIPTS[phase]; req(src.is_file() and not src.is_symlink(),"sbatch source unsafe")
    original=src.read_text(); req(OLD_ROOT in original,"unexpected frozen sbatch root")
    lines=original.splitlines(); directives=[x for x in lines[1:] if x.startswith("#SBATCH")]
    body="\n".join(x for x in lines[1:] if not x.startswith("#SBATCH"))
    body=body.replace(OLD_ROOT,str(run))
    head=["#!/usr/bin/env bash",*[(x.replace(OLD_ROOT,str(run))) for x in directives],"set -euo pipefail",
      "set -- "+" ".join(shlex.quote(x) for x in [h8,h7,*args]),
      '[[ "$#" -ge 2 && "$1" == "'+h8+'" && "$2" == "'+h7+'" ]] || exit 91','shift 2',
      f"export H8_PAYLOAD_SHA256={h8} H7_PAYLOAD_SHA256={h7} H8_PACKAGE_ROOT={package} H8_RUN_ROOT={run} H8_STAGE_SNAPSHOT={snapshot} H8_PHASE={phase}",
      f"(cd {shlex.quote(str(snapshot))} && sha256sum -c {H8_MANIFEST}) >/dev/null",
      f"(cd {shlex.quote(str(run))} && sha256sum -c {H8_MANIFEST}) >/dev/null",
      "h8_post(){ rc=$?; (cd \"$H8_STAGE_SNAPSHOT\" && sha256sum -c "+H8_MANIFEST+") >/dev/null || rc=92; (cd \"$H8_RUN_ROOT\" && sha256sum -c "+H8_MANIFEST+") >/dev/null || rc=93; mkdir -p \"$H8_RUN_ROOT/h8_receipts\"; chmod 700 \"$H8_RUN_ROOT/h8_receipts\"; python3 - \"$rc\" <<'H8PY'\nimport json,os,sys\nif int(sys.argv[1])==0:\n p=os.path.join(os.environ['H8_RUN_ROOT'],'h8_receipts',os.environ['H8_PHASE']+'-'+os.environ['SLURM_JOB_ID']+'.json')\n v={'phase':os.environ['H8_PHASE'],'h8':os.environ['H8_PAYLOAD_SHA256'],'h7':os.environ['H7_PAYLOAD_SHA256'],'package_root':os.environ['H8_PACKAGE_ROOT'],'run_root':os.environ['H8_RUN_ROOT'],'status':'PASS_H8_RUNTIME_PRE_POST'}\n open(p,'x').write(json.dumps(v,sort_keys=True)+'\\n'); os.chmod(p,0o600)\nH8PY\nexit $rc; }; trap h8_post EXIT"]
    return ("\n".join(head)+"\n"+body+"\n").encode()

def submit(*,package:Path,run:Path,phase:str,h8:str,h7:str,args:list[str],dependency:str|None,sbatch="sbatch") -> dict:
    package,run=safe_roots(package,run); verify_package(package,h8,h7); run.mkdir(mode=0o700,parents=True,exist_ok=True); seed_or_verify_run(package,run,h8)
    idx=PHASES.index(phase)
    if idx:
        req(dependency and dependency.isdecimal(),"missing downstream dependency")
        previous=PHASES[idx-1]
        if previous == "production":
            found=sorted((run/"h8_receipts").glob(f"production-{dependency}_*.json"))
            req(len(found)==480,"missing production runtime receipts downstream")
            for path in found: validate_receipt(path,"production",h8,h7,package,run)
        else: validate_receipt(receipt_path(run,previous,dependency),previous,h8,h7,package,run)
    snap=make_snapshot(package,run,phase,h8); data=render(package,run,snap,phase,h8,h7,args)
    verify_package(package,h8,h7); verify_package(snap,h8,h7,file_mode=0o400,dir_mode=0o500)
    cmd=[sbatch,"--parsable",f"--export=ALL,H8_PAYLOAD_SHA256={h8},H7_PAYLOAD_SHA256={h7},H8_PHASE={phase}"]+([f"--dependency=afterok:{dependency}"] if dependency else [])
    cp=subprocess.run(cmd,input=data,capture_output=True,check=True); job=cp.stdout.decode().strip().split(";")[0]; req(job.isdecimal(),"sbatch returned nondecimal job")
    out={"phase":phase,"job_id":job,"h8":h8,"h7":h7,"package_root":str(package),"run_root":str(run),"snapshot":str(snap),"submitted_bytes_sha256":hashlib.sha256(data).hexdigest(),"argv":cmd,"stdin_submission":True}
    d=run/"h8_submissions"; d.mkdir(mode=0o700,exist_ok=True); (d/f"{phase}-{job}.json").write_text(json.dumps(out,sort_keys=True)+"\n"); return out

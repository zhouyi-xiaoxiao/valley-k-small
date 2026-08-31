#!/usr/bin/env python3
"""Hash-pinned dynamic-afterok submitter with no-overwrite readback receipt."""
import argparse,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
SCRIPTS={"canary":"isambard_ai_gating_v4_r2_gpu_canary.sbatch","production":"isambard_ai_gating_v4_r2_fullnode.sbatch","reducer":"isambard_ai_gating_v4_r2_reduce.sbatch","replay":"isambard_ai_gating_v4_r2_replay.sbatch","combined":"isambard_ai_gating_v4_r2_combined.sbatch"}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--phase",choices=tuple(SCRIPTS),required=True);p.add_argument("--dependency",required=True);p.add_argument("--payload-sha256",required=True);p.add_argument("--receipt",type=Path,required=True);p.add_argument("args",nargs=argparse.REMAINDER);a=p.parse_args()
 if not re.fullmatch(r"[0-9]+",a.dependency) or not re.fullmatch(r"[0-9a-f]{64}",a.payload_sha256):raise SystemExit(2)
 payload=ROOT/"notes/isambard_ai_v4_r2_payload.sha256";script=ROOT/"code"/SCRIPTS[a.phase]
 if sha(payload)!=a.payload_sha256 or not script.is_file() or script.is_symlink() or a.receipt.exists():raise SystemExit(2)
 args=a.args[1:] if a.args[:1]==["--"] else a.args;command=["sbatch","--parsable",f"--dependency=afterok:{a.dependency}",str(script.relative_to(ROOT)),*args]
 cp=subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True);job=cp.stdout.strip().split(";")[0]
 if not job.isdigit():raise SystemExit("nondecimal sbatch job ID")
 readback=subprocess.run(["scontrol","show","job","-o",job],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
 if f"Dependency=afterok:{a.dependency}" not in readback or f"WorkDir={ROOT}" not in readback:raise SystemExit("scontrol dependency/workdir readback drift")
 data={"schema":"grid2d-one-two-target-gating-v4-r2-submission-receipt-v1","phase":a.phase,"job_id":job,"dependency_afterok":a.dependency,"payload_manifest_sha256":a.payload_sha256,"sbatch":{"path":str(script.relative_to(ROOT)),"sha256":sha(script),"argv":command},"scontrol_readback":readback}
 a.receipt.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(data,indent=2,sort_keys=True)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".submit.",dir=a.receipt.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(raw);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,a.receipt)
 finally:tmp.unlink(missing_ok=True)
 print(json.dumps({"status":"SUBMITTED_WITH_READBACK","phase":a.phase,"job_id":job,"receipt_sha256":sha(a.receipt)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

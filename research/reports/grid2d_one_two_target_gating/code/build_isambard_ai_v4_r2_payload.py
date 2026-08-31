#!/usr/bin/env python3
"""Build/verify exact append-only v4-r2 payload inventory."""
import argparse,hashlib,os,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"notes/isambard_ai_v4_r2_payload.sha256"
MEMBERS=(
"artifacts/data/disorder_field_pack_v4_r2_reflect.npz","artifacts/data/disorder_field_pack_v4_r2_reflect.manifest.json","artifacts/data/gating_v4_r2_production_manifest.json",
"code/analyze_gpu_gating_v3_secondary_r1.py","code/analyze_gpu_gating_v4_r2_combined.py","code/build_gating_campaign_manifest_v4_r2.py","code/build_isambard_ai_v4_r2_payload.py","code/capture_gpu_lane_v4_r2.py","code/generate_disorder_field_pack_v4_r2.py","code/gpu_gating_mc_v3.py","code/gpu_gating_mc_v4_r2.py","code/independent_replay_gpu_gating_v4_r2.py","code/isambard_ai_gating_v4_r2_combined.sbatch","code/isambard_ai_gating_v4_r2_fullnode.sbatch","code/isambard_ai_gating_v4_r2_gpu_canary.sbatch","code/isambard_ai_gating_v4_r2_reduce.sbatch","code/isambard_ai_gating_v4_r2_replay.sbatch","code/reduce_gpu_gating_v3.py","code/reduce_gpu_gating_v4_r2.py","code/submit_isambard_ai_gating_v4_r2.py","code/test_isambard_ai_gating_v4_r2.py","code/validate_gating_campaign_manifest_v4_r2.py","code/verify_gpu_canary_v4_r2.py","code/verify_v3_release_for_v4_r2.py","notes/isambard_ai_v4_payload.sha256","notes/isambard_ai_v4_r2_amendment.md")
def sha(p:Path)->str:
 d=hashlib.sha256()
 with p.open("rb") as h:
  for c in iter(lambda:h.read(1<<20),b""):d.update(c)
 return d.hexdigest()
def lines():
 out=[]
 for rel in MEMBERS:
  p=ROOT/rel
  if not p.is_file() or p.is_symlink():raise ValueError(f"missing/symlink {rel}")
  out.append(f"{sha(p)}  {rel}")
 return out
def verify()->str:
 if OUT.read_text().splitlines()!=lines():raise ValueError("r2 payload drift")
 return sha(OUT)
def build()->str:
 if OUT.exists():raise FileExistsError("r2 payload append-only")
 data=("\n".join(lines())+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v4r2-payload.",dir=OUT.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,OUT)
 finally:tmp.unlink(missing_ok=True)
 return verify()
def main():
 p=argparse.ArgumentParser();p.add_argument("--verify",action="store_true");a=p.parse_args();print(verify() if a.verify else build());return 0
if __name__=="__main__":raise SystemExit(main())

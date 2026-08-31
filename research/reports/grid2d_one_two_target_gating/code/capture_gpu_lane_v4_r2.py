#!/usr/bin/env python3
"""Capture one Slurm GPU lane identity as no-overwrite JSON."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--lane",type=int,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 if a.lane not in range(4) or a.output.exists():raise SystemExit(2)
 cp=subprocess.run(["nvidia-smi","--query-gpu=index,uuid,pci.bus_id,name,driver_version","--format=csv,noheader,nounits"],check=True,capture_output=True,text=True)
 rows=[[x.strip() for x in line.split(",")] for line in cp.stdout.splitlines() if line.strip()]
 if len(rows)!=1 or len(rows[0])!=5:raise SystemExit(f"lane {a.lane} did not see exactly one physical GPU")
 payload={"schema":"grid2d-one-two-target-gating-v4-r2-gpu-lane-v1","lane":a.lane,"cuda_visible_devices":os.environ.get("CUDA_VISIBLE_DEVICES"),"slurm_job_id":os.environ.get("SLURM_JOB_ID"),"slurm_step_id":os.environ.get("SLURM_STEP_ID"),"gpu":{"index":rows[0][0],"uuid":rows[0][1],"pci_bus_id":rows[0][2],"name":rows[0][3],"driver_version":rows[0][4]}}
 if not payload["cuda_visible_devices"]:raise SystemExit("empty CUDA_VISIBLE_DEVICES")
 a.output.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(payload,sort_keys=True,indent=2)+"\n").encode();fd,name=tempfile.mkstemp(prefix=f".lane-{a.lane}.",dir=a.output.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,a.output)
 finally:tmp.unlink(missing_ok=True)
 return 0
if __name__=="__main__":raise SystemExit(main())

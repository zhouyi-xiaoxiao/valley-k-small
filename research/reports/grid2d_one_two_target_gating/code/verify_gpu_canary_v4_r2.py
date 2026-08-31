#!/usr/bin/env python3
"""Verify four isolated physical GPU identities and issue a PASS receipt."""
import argparse,hashlib,json,os,tempfile
from pathlib import Path
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--lanes",type=Path,required=True);p.add_argument("--release-receipt",type=Path,required=True);p.add_argument("--release-sha256",required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 if sha(a.release_receipt)!=a.release_sha256:raise SystemExit("release receipt hash drift")
 release=json.loads(a.release_receipt.read_text());
 if release.get("status")!="PASS_AUTHORIZE_V4_R2_HARDWARE_CANARY":raise SystemExit("release did not authorize canary")
 expected={f"lane-{i}.json" for i in range(4)};members={x.name for x in a.lanes.iterdir()}
 if members!=expected:raise SystemExit("lane exact inventory drift")
 rows=[]
 for i in range(4):
  path=a.lanes/f"lane-{i}.json";st=path.lstat()
  if path.is_symlink() or not path.is_file() or st.st_nlink!=1:raise SystemExit("lane member is not independent regular file")
  value=json.loads(path.read_text());
  if value.get("schema")!="grid2d-one-two-target-gating-v4-r2-gpu-lane-v1" or value.get("lane")!=i:raise SystemExit("lane schema/index drift")
  rows.append(value)
 uuids={x["gpu"]["uuid"] for x in rows};pci={x["gpu"]["pci_bus_id"] for x in rows};visible={x["cuda_visible_devices"] for x in rows}
 if len(uuids)!=4 or len(pci)!=4 or len(visible)!=4:raise SystemExit("four distinct UUID/PCI/CUDA assignments not proven")
 payload={"schema":"grid2d-one-two-target-gating-v4-r2-gpu-canary-v1","status":"PASS_AUTHORIZE_V4_R2_PRODUCTION","release_receipt_sha256":a.release_sha256,"lanes":[{"lane":x["lane"],"cuda_visible_devices":x["cuda_visible_devices"],"uuid":x["gpu"]["uuid"],"pci_bus_id":x["gpu"]["pci_bus_id"],"capture_sha256":sha(a.lanes/f"lane-{x['lane']}.json")} for x in rows],"distinct_uuid_count":4,"distinct_pci_count":4,"distinct_cuda_visible_devices_count":4}
 if a.output.exists():raise SystemExit("canary receipt exists")
 data=(json.dumps(payload,sort_keys=True,indent=2)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".canary.",dir=a.output.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,a.output)
 finally:tmp.unlink(missing_ok=True)
 print(json.dumps({"status":payload["status"],"sha256":sha(a.output)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the append-only reflect-mode 128-field v4-r2 pack."""

from __future__ import annotations
import argparse, hashlib, io, json, math, os, tempfile, zipfile
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter

SCHEMA="grid2d-one-two-target-gating-disorder-field-pack-v4-r2"
N,H,W,SIGMA=128,48,64,4.0
BASE,STRIDE=8_202_607_270_000,1_000_003
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"artifacts/data/disorder_field_pack_v4_r2_reflect.npz"
SIDECAR=ROOT/"artifacts/data/disorder_field_pack_v4_r2_reflect.manifest.json"

def sha_bytes(v:bytes)->str:return hashlib.sha256(v).hexdigest()
def sha_file(p:Path)->str:
 d=hashlib.sha256()
 with p.open("rb") as h:
  for c in iter(lambda:h.read(1<<20),b""):d.update(c)
 return d.hexdigest()
def normalize(a:np.ndarray)->np.ndarray:
 a=np.asarray(a,dtype="<f8").copy(order="C");a-=float(a.mean());a/=float(np.max(np.abs(a)))
 f=a.reshape(-1);anchor=int(np.argmax(np.abs(f)));f[anchor]=math.copysign(1.0,float(f[anchor]))
 candidates=np.delete(np.arange(f.size),anchor);fix=int(candidates[np.argmin(np.abs(f[candidates]))])
 for _ in range(32):
  r=math.fsum(map(float,f))
  if r==0.0:break
  f[fix]=float(f[fix])-r
 if math.fsum(map(float,f))!=0.0 or float(np.max(np.abs(f)))!=1.0:raise ArithmeticError("normalization failed")
 return a
def field(i:int)->tuple[int,np.ndarray]:
 seed=BASE+STRIDE*i;rng=np.random.Generator(np.random.PCG64(seed))
 return seed,normalize(gaussian_filter(rng.standard_normal((H,W),dtype=np.float64),sigma=SIGMA,mode="reflect",truncate=4.0))
def npy(a:np.ndarray)->bytes:
 b=io.BytesIO();np.lib.format.write_array(b,np.ascontiguousarray(a),allow_pickle=False);return b.getvalue()
def build(pack:Path,sidecar:Path)->dict:
 if pack.exists() or sidecar.exists():raise FileExistsError("r2 outputs are append-only")
 pack.parent.mkdir(parents=True,exist_ok=True);contrasts=np.empty((N,H,W),dtype="<f8");seeds=np.empty(N,dtype="<i8");records=[]
 for i in range(N):
  seed,a=field(i);seeds[i]=seed;contrasts[i]=a;records.append({"index":i,"seed":seed,"sha256_float64_le":sha_bytes(a.tobytes()),"exact_sum_fsum":math.fsum(map(float,a.reshape(-1))),"max_abs":float(np.max(np.abs(a)))})
 fd,name=tempfile.mkstemp(prefix=".v4r2.",dir=pack.parent);os.close(fd);tmp=Path(name)
 try:
  with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_STORED) as z:
   for n,a in (("contrasts",contrasts),("seeds",seeds),("sigma",np.asarray(SIGMA,dtype="<f8"))):
    info=zipfile.ZipInfo(f"{n}.npy",(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED;info.create_system=3;info.external_attr=0o600<<16;z.writestr(info,npy(a))
  os.link(tmp,pack)
 finally:tmp.unlink(missing_ok=True)
 payload={"schema":SCHEMA,"definition":{"shape":[N,H,W],"sigma":SIGMA,"rng":"NumPy PCG64","seed_base":BASE,"seed_stride":STRIDE,"smoothing":{"function":"scipy.ndimage.gaussian_filter","mode":"reflect","truncate":4.0},"normalization":"exact math.fsum zero and exact maxabs one","distribution_binding":"same construction as frozen v3"},"pack":{"filename":pack.name,"sha256":sha_file(pack)},"fields":records,"generator":{"filename":Path(__file__).name,"sha256":sha_file(Path(__file__))}}
 data=(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v4r2-sidecar.",dir=sidecar.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.link(tmp,sidecar)
 finally:tmp.unlink(missing_ok=True)
 return payload
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--pack",type=Path,default=PACK);p.add_argument("--sidecar",type=Path,default=SIDECAR);a=p.parse_args();x=build(a.pack.absolute(),a.sidecar.absolute());print(json.dumps({"status":"PASS","sha256":x["pack"]["sha256"]}));return 0
if __name__=="__main__":raise SystemExit(main())

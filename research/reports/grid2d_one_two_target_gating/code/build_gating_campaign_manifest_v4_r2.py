#!/usr/bin/env python3
"""Build and validate the full scientific v4-r2 production manifest."""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, tempfile
from pathlib import Path
from typing import Any,Mapping
import numpy as np
import reduce_gpu_gating_v3 as reducer_core

SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-manifest"
RESULT_SCHEMA="grid2d-one-two-target-gating-fixed-mean-gpu-v4-r2"
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"artifacts/data"
PACK=DATA/"disorder_field_pack_v4_r2_reflect.npz";SIDECAR=DATA/"disorder_field_pack_v4_r2_reflect.manifest.json";OUTPUT=DATA/"gating_v4_r2_production_manifest.json"
V3_PACK=DATA/"disorder_field_pack_v3.npz";V3_SIDECAR=DATA/"disorder_field_pack_v3.manifest.json"
CONTAINER={"reference":"/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif","sha256":"aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4"}
GEOMETRIES=tuple((x,y) for x in (24,32,40) for y in (9,16,24,31,38));AMPLITUDES=(0.,.05,.1,.15,.2,.25)

def sha(p:Path)->str:
 d=hashlib.sha256()
 with p.open("rb") as h:
  for c in iter(lambda:h.read(1<<20),b""):d.update(c)
 return d.hexdigest()
def load(p:Path)->dict:
 return json.loads(p.read_text(encoding="utf-8"))
def walk_seed(f:int,s:int)->int:return 12_000_000_000+104_729*f+1_009*s
def cells()->list[dict[str,Any]]:
 out=[]
 for x,y in GEOMETRIES:
  for amplitude in AMPLITUDES:
   for f in range(128):
    for s in (0,1):out.append({"cell_id":len(out),"target2_x":x,"target2_y":y,"amplitude":amplitude,"disorder_replicate":f,"walk_replicate":s,"walk_seed":walk_seed(f,s)})
 return out
def prereg()->dict[str,Any]:
 p=copy.deepcopy(load(DATA/"gating_v3_production_manifest.json")["preregistration"])
 p["field_count"]=128;p["production_task_count"]=23040
 p["randomness"]["effective_field_blocks"]=128
 for stage in p["stages"]:
  if stage["stage_id"]=="G0":continue
  stage["task_count"]*=4;stage["expected_node_hours"]=round(float(stage["expected_node_hours"])*4,3);stage["hard_cap_node_hours"]=round(float(stage["hard_cap_node_hours"])*4,3)
 p["budget"].update({"optional_precision_expected_range":[136.0,516.0],"optional_precision_hard_cap":640.0,"reserve":200.0,"stage_hard_cap_total":2842.0,"campaign_hard_cap":3794.0,"unallocated_margin":112.0})
 p["status"]="v4-r2-frozen-before-any-reflect-pack-production-result"
 p["randomness"]["walk_seed_formula"]="12000000000 + disorder_replicate * 104729 + walk_replicate * 1009"
 p["randomness"]["v3_distribution_binding"]="independent seeds; identical PCG64 Gaussian reflect-mode sigma-4 field construction"
 p["v4_r2_fullnode"]={"protocol_id":"grid2d_one_two_target_gating_isambard_ai_v4_r2_20260727","array_tasks":480,"concurrency":240,"gpus_per_node":4,"cells_per_allocation":48,"cells_per_gpu":12,"cell_formula":"t + 480 * (g + 4*k)","wall_seconds":7200,"reservation_ceiling_nhr":960,"release_jobs":["5788357","5788358","5789031"],"requires_v3_release_receipt":True,"requires_distinct_gpu_canary_receipt":True,"requires_independent_raw_replay":True}
 p["combined_analysis"]={"v4_only":{"blocks":128,"bit_generator":"PCG64","seed":2026072700,"resamples":20000},"pooled":{"blocks":160,"bit_generator":"PCG64","seed":2026072701,"resamples":20000,"critical_order_statistic_one_indexed":19001},"primary":{"geometry":{"target2_x":32,"target2_y":24},"contrast":{"high":.2,"low":0.,"direction":"high-low"},"confidence_level":.95,"pooled_df":159,"rope":[-.002,.002]}}
 p["initial_v4_wrap_boundary"]={"payload_sha256":"3752b36338c732483b0aa739331abbff0e9999be8f4c83ad34461d65ef856485","field_pack_sha256":"b4a2a4a21621a681f73cb653d84dd9d127394732b73edb8cb7b4fce5c592d68d","classification":"sensitivity-only; forbidden from v3 pooling"}
 return p
def validate(m:Mapping[str,Any],pack:Path,sidecar:Path,v3_pack:Path,v3_sidecar:Path,runner:Path,engine:Path)->dict:
 if m.get("schema")!=SCHEMA or m.get("campaign")!={"kind":"production","cell_count":23040,"domain":{"width":64,"height":48}}:raise ValueError("campaign/schema drift")
 expected_defaults={"walkers":1_000_000,"steps":80_000,"batch_size":131_072,"base_hold":.30,"target_radius":3,"start_x":7,"start_y":24,"target1_x":54,"target1_y":24,"checkpoints":[5000,10000,20000,40000,80000],"seed_base":12_000_000_000}
 if m.get("defaults")!=expected_defaults or m.get("profiles")!={"tail_160k":{"steps":160000,"checkpoints":[10000,20000,40000,80000,160000]}}:raise ValueError("defaults/profiles drift")
 if m.get("preregistration")!=prereg():raise ValueError("full inherited preregistration drift")
 contract=reducer_core._campaign_contract(m)
 if contract["primary_target2"]!=(32,24) or contract["tail_anchors"]!=((24,24),(32,24),(40,24)):raise ValueError("v3 reducer contract incompatibility")
 if m.get("cells")!=cells():raise ValueError("cell inventory drift")
 side=load(sidecar);v3side=load(v3_sidecar)
 with np.load(pack,allow_pickle=False) as z:a=np.asarray(z["contrasts"],dtype="<f8");seeds=np.asarray(z["seeds"],dtype="<i8")
 with np.load(v3_pack,allow_pickle=False) as z:v3a=np.asarray(z["contrasts"],dtype="<f8");v3seeds=np.asarray(z["seeds"],dtype="<i8")
 if a.shape!=(128,48,64) or side.get("definition",{}).get("smoothing",{}).get("mode")!="reflect":raise ValueError("r2 reflect pack drift")
 if seeds.tolist()!=[8_202_607_270_000+1_000_003*i for i in range(128)]:raise ValueError("r2 field seed drift")
 if set(map(int,seeds))&set(map(int,v3seeds)):raise ValueError("v3/r2 field seed collision")
 r2walk={walk_seed(i,s) for i in range(128) for s in (0,1)};v3walk={1729+104729*i+1009*s for i in range(32) for s in (0,1)}
 if len(r2walk)!=256 or r2walk&v3walk:raise ValueError("v3/r2 walk seed collision")
 r2hash={r["sha256_float64_le"] for r in side["fields"]};v3hash={r["sha256_float64_le"] for r in v3side["fields"]}
 if len(r2hash)!=128 or r2hash&v3hash:raise ValueError("v3/r2 field content collision")
 if not all(math.fsum(map(float,x.reshape(-1)))==0 and float(np.max(np.abs(x)))==1 for x in a):raise ValueError("field normalization drift")
 expected_artifacts={"field_pack":{"filename":pack.name,"sha256":sha(pack),"sidecar_filename":sidecar.name,"sidecar_sha256":sha(sidecar)},"v3_distribution_reference":{"field_pack_sha256":sha(v3_pack),"sidecar_sha256":sha(v3_sidecar),"smoothing_mode":"reflect"},"runner_source":{"filename":runner.name,"sha256":sha(runner)},"runner_engine":{"filename":engine.name,"sha256":sha(engine)},"container":CONTAINER,"result_schema":RESULT_SCHEMA}
 if m.get("field_pack_sha256")!=sha(pack) or m.get("artifacts")!=expected_artifacts:raise ValueError("artifact inventory drift")
 return {"status":"PASS_V4_R2_MANIFEST","cells":23040,"fields":128,"campaign_contract":contract}
def build(pack:Path=PACK,sidecar:Path=SIDECAR,output:Path=OUTPUT)->dict:
 if output.exists():raise FileExistsError("r2 manifest append-only")
 runner=Path(__file__).with_name("gpu_gating_mc_v4_r2.py");engine=Path(__file__).with_name("gpu_gating_mc_v3.py")
 m={"schema":SCHEMA,"campaign":{"kind":"production","cell_count":23040,"domain":{"width":64,"height":48}},"defaults":{"walkers":1_000_000,"steps":80_000,"batch_size":131_072,"base_hold":.3,"target_radius":3,"start_x":7,"start_y":24,"target1_x":54,"target1_y":24,"checkpoints":[5000,10000,20000,40000,80000],"seed_base":12_000_000_000},"profiles":{"tail_160k":{"steps":160000,"checkpoints":[10000,20000,40000,80000,160000]}},"field_pack_sha256":sha(pack),"artifacts":{"field_pack":{"filename":pack.name,"sha256":sha(pack),"sidecar_filename":sidecar.name,"sidecar_sha256":sha(sidecar)},"v3_distribution_reference":{"field_pack_sha256":sha(V3_PACK),"sidecar_sha256":sha(V3_SIDECAR),"smoothing_mode":"reflect"},"runner_source":{"filename":runner.name,"sha256":sha(runner)},"runner_engine":{"filename":engine.name,"sha256":sha(engine)},"container":CONTAINER,"result_schema":RESULT_SCHEMA},"preregistration":prereg(),"cells":cells()}
 validate(m,pack,sidecar,V3_PACK,V3_SIDECAR,runner,engine);output.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(m,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v4r2-manifest.",dir=output.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.link(tmp,output)
 finally:tmp.unlink(missing_ok=True)
 return m
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--build",action="store_true");p.add_argument("--manifest",type=Path,default=OUTPUT);a=p.parse_args();m=build() if a.build else load(a.manifest);s=validate(m,PACK,SIDECAR,V3_PACK,V3_SIDECAR,Path(__file__).with_name("gpu_gating_mc_v4_r2.py"),Path(__file__).with_name("gpu_gating_mc_v3.py"));print(json.dumps(s,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

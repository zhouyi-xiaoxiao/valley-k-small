#!/usr/bin/env python3
"""Hardened v3 release: base scientific replay plus exact canary reduction."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,tempfile
from pathlib import Path
from typing import Any
import numpy as np
import verify_v3_release_for_v4_r2 as base

CANARY_MANIFEST_SHA="5c056e20fc45c97f6e8d444ecdb9b63c334483ceb8461387d83d3e1612873fe4"
OUT=base.R2_ROOT/"artifacts/releases/v3-release-for-v4-r2-h1.json"
RELEASE_KEYS={"schema","status","fixed_roots","fixed_jobs","fixed_contracts","evidence_hashes","inventory_digest","raw_replay","live_sacct_query_sha256","secondary_result_schema","secondary_result_status","canary_reduction"}
def req(v:bool,m:str)->None:
 if not v:raise ValueError(m)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def strict_json(path:Path,*,mode600:bool=False)->dict[str,Any]:
 st=path.lstat();req(path.is_file() and not path.is_symlink() and st.st_nlink==1,"unsafe JSON file")
 if mode600:req(st.st_mode&0o777==0o600,"authority JSON mode drift")
 def hook(pairs):
  out={}
  for key,value in pairs:req(key not in out,f"duplicate JSON key {key}");out[key]=value
  return out
 value=json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=hook,parse_constant=lambda token:(_ for _ in ()).throw(ValueError(f"nonfinite JSON {token}")))
 req(isinstance(value,dict),"JSON root not object");return value
def replay_canary_sacct(path:Path,inventory:list[dict[str,Any]])->dict[str,Any]:
 with path.open(newline="",encoding="utf-8") as handle:
  reader=csv.DictReader(handle,delimiter="|");rows=list(reader);header=reader.fieldnames
 req(header==["JobIDRaw","JobID","State","ExitCode"],"canary sacct exact header drift")
 by_task={int(row["slurm_array_task_id"]):str(row["slurm_job_id"]) for row in inventory}
 req(set(by_task)==set(range(8)) and len(set(by_task.values()))==8,"canary allocation inventory drift")
 matched={};parents=0
 for row in rows:
  req(set(row)==set(header) and all(value is not None for value in row.values()),"canary sacct row shape drift")
  ids={row["JobIDRaw"],row["JobID"]}
  if ids=={"5788354"}:
   parents+=1;req(row["State"].split("+")[0]=="COMPLETED" and row["ExitCode"]=="0:0","canary parent not completed")
   continue
  candidates=[task for task,job in by_task.items() if job in ids or f"5788354_{task}" in ids]
  req(len(candidates)==1,"canary sacct unexpected/ambiguous allocation row")
  task=candidates[0];req(task not in matched,"duplicate canary sacct allocation")
  req(row["State"].split("+")[0]=="COMPLETED" and row["ExitCode"]=="0:0",f"canary task {task} not COMPLETED/0:0")
  matched[task]=row
 req(parents==1 and set(matched)==set(range(8)) and len(rows)==9,"canary sacct exact 8-task plus parent inventory drift")
 return {"independently_parsed":True,"parent_rows":1,"allocations":8,"cells":8,"cells_per_allocation":1,"state":"COMPLETED","exit_code":"0:0","receipt_sha256":sha(path)}
def replay_canary_raw(json_path:Path,npz_path:Path,manifest:dict[str,Any],config:dict[str,Any],inventory:dict[str,Any])->None:
 cell=int(config["cell_id"]);payload=strict_json(json_path,mode600=True)
 req(set(payload)=={"schema","manifest","parameters","domain","rng","field","one_target","two_targets","paired_outcomes","cumulative_counts","histograms","gates","gating_probability_drop","gating_probability_ratio","target2_first_probability","provenance","runtime"},f"canary raw {cell} exact top keys drift")
 req(payload["schema"]=="grid2d-one-two-target-gating-fixed-mean-gpu-v3",f"canary raw {cell} schema drift")
 mr=payload["manifest"];req(isinstance(mr,dict) and set(mr)=={"filename","sha256","schema","cell_id","profile"} and mr=={"filename":"gating_v3_canary_manifest.json","sha256":CANARY_MANIFEST_SHA,"schema":"grid2d-one-two-target-gating-gpu-v3-manifest","cell_id":cell,"profile":None},f"canary raw {cell} manifest reverse bind drift")
 defaults=manifest["defaults"];parameters=payload["parameters"];expected={"walkers":defaults["walkers"],"steps":defaults["steps"],"batch_size":defaults["batch_size"],"base_hold":defaults["base_hold"],"amplitude":config["amplitude"],"target_radius":defaults["target_radius"],"disorder_replicate":config["disorder_replicate"],"walk_replicate":config["walk_replicate"],"checkpoints":defaults["checkpoints"]}
 req(isinstance(parameters,dict) and set(parameters)==set(expected)|{"disorder_seed"} and all(parameters[key]==value for key,value in expected.items()) and isinstance(parameters["disorder_seed"],int) and not isinstance(parameters["disorder_seed"],bool),f"canary raw {cell} parameters drift")
 domain=payload["domain"];req(isinstance(domain,dict) and set(domain)=={"source","width","height","boundary","start","target1","target2","absorbing_precedence"} and domain.get("start")=={"x":defaults["start_x"],"y":defaults["start_y"]} and domain.get("target1")=={"x":defaults["target1_x"],"y":defaults["target1_y"]} and domain.get("target2")=={"x":config["target2_x"],"y":config["target2_y"]},f"canary raw {cell} domain drift")
 rng=payload["rng"];expected_seed=defaults["seed_base"]+104729*config["disorder_replicate"]+1009*config["walk_replicate"]
 req(isinstance(rng,dict) and set(rng)=={"algorithm","walk_seed","walk_seed_origin","disorder_stride","walk_stride","batch_seed_rule","common_random_numbers","deterministic_for_fixed_manifest_runtime_device"} and rng.get("walk_seed")==expected_seed and rng.get("walk_seed_origin")=="v2_common_random_number_formula" and rng.get("batch_seed_rule")=="walk_seed_plus_batch_start" and rng.get("common_random_numbers") is True,f"canary raw {cell} RNG drift")
 field=payload["field"];req(field.get("pack_filename")=="disorder_field_pack_v3.npz" and field.get("pack_sha256")=="d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420" and field.get("expected_pack_sha256")==field.get("pack_sha256"),f"canary raw {cell} field binding drift")
 provenance=payload["provenance"];req(isinstance(provenance,dict) and set(provenance)=={"source","source_sha256","argv","slurm"},f"canary raw {cell} provenance keys drift");slurm=provenance.get("slurm",{});req(isinstance(slurm,dict) and set(slurm)=={"SLURM_JOB_ID","SLURM_ARRAY_JOB_ID","SLURM_ARRAY_TASK_ID","SLURM_JOB_NAME","SLURM_NODELIST","SLURM_CPUS_PER_TASK","SLURM_JOB_ACCOUNT","SLURM_JOB_PARTITION"} and provenance.get("source")=="gpu_gating_mc_v3.py" and provenance.get("source_sha256")==manifest["artifacts"]["runner_source"]["sha256"] and slurm.get("SLURM_ARRAY_JOB_ID")=="5788354" and slurm.get("SLURM_ARRAY_TASK_ID")==str(cell) and slurm.get("SLURM_JOB_ID")==inventory["slurm_job_id"],f"canary raw {cell} source/Slurm drift")
 hist=payload["histograms"];req(isinstance(hist,dict) and set(hist)=={"format","path","sha256","dtype","fpt_index_range_inclusive","arrays"} and hist.get("path")==npz_path.name and hist.get("sha256")==sha(npz_path) and hist.get("dtype")=="int64",f"canary raw {cell} NPZ reverse bind drift")
 req(payload["gates"].get("all_passed") is True,f"canary raw {cell} scientific gates failed")
 with np.load(npz_path,allow_pickle=False) as archive:
  keys={"schema_version","one_target1_fpt_histogram","two_target1_fpt_histogram","two_target2_fpt_histogram","checkpoint_steps","checkpoint_counts","paired_outcome_counts"};req(set(archive.files)==keys,f"canary raw {cell} NPZ keys drift");arrays={key:np.asarray(archive[key]) for key in keys}
 steps=defaults["steps"];checkpoints=defaults["checkpoints"];shapes={"schema_version":(),"one_target1_fpt_histogram":(steps+1,),"two_target1_fpt_histogram":(steps+1,),"two_target2_fpt_histogram":(steps+1,),"checkpoint_steps":(len(checkpoints),),"checkpoint_counts":(len(checkpoints),6),"paired_outcome_counts":(3,3)}
 for key,array in arrays.items():req(array.dtype==np.dtype(np.int64) and array.shape==shapes[key] and bool(np.all(array>=0)),f"canary raw {cell} {key} dtype/shape/sign drift")
 req(int(arrays["schema_version"])==3 and arrays["checkpoint_steps"].tolist()==checkpoints,f"canary raw {cell} NPZ schema/checkpoints drift")
 walkers=defaults["walkers"];one=arrays["one_target1_fpt_histogram"];two1=arrays["two_target1_fpt_histogram"];two2=arrays["two_target2_fpt_histogram"];checks=arrays["checkpoint_counts"];paired=arrays["paired_outcome_counts"]
 req(int(paired.sum(dtype=np.int64))==walkers and int(paired[0,1])==0 and bool(np.all(paired[2,:]==0)),f"canary raw {cell} paired mass/state drift")
 one_hits=int(one.sum(dtype=np.int64));two1_hits=int(two1.sum(dtype=np.int64));two2_hits=int(two2.sum(dtype=np.int64));req(one_hits==int(paired[1,:].sum()) and two1_hits==int(paired[:,1].sum()) and two2_hits==int(paired[:,2].sum()),f"canary raw {cell} histogram/paired mass drift")
 req(bool(np.all(checks[:,0]+checks[:,1]==walkers)) and bool(np.all(checks[:,2]+checks[:,3]+checks[:,4]==walkers)) and bool(np.all(checks[:,5]==walkers)),f"canary raw {cell} checkpoint mass drift")
 req(checks[-1].tolist()==[one_hits,walkers-one_hits,two1_hits,two2_hits,walkers-two1_hits-two2_hits,walkers],f"canary raw {cell} final checkpoint drift")
 req(payload["one_target"].get("target1",{}).get("hits")==one_hits and payload["two_targets"].get("target1",{}).get("hits")==two1_hits and payload["two_targets"].get("target2",{}).get("hits")==two2_hits and payload["gating_probability_drop"]==(one_hits-two1_hits)/walkers,f"canary raw {cell} JSON/NPZ statistic drift")
def validate_canary(manifest:Path,raw:Path,reduction_dir:Path)->dict[str,Any]:
 req(sha(manifest)==CANARY_MANIFEST_SHA,"canary manifest SHA drift");members={x.name for x in reduction_dir.iterdir()};req(members=={"reduction.json","reduction.csv","sacct-canary-5788353.psv"},"canary reduction exact members drift")
 rj=reduction_dir/"reduction.json";rc=reduction_dir/"reduction.csv";sacct=reduction_dir/"sacct-canary-5788353.psv"
 for p in (rj,rc,sacct):
  st=p.lstat();req(p.is_file() and not p.is_symlink() and st.st_nlink==1 and st.st_mode&0o777==0o600,"canary reduction unsafe mode/link")
 value=strict_json(rj,mode600=True);req(rj.read_text(encoding="utf-8")==json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n","canary reduction JSON is not canonical");req(set(value)=={"schema","mode","audit","inventory","inventory_decision","csv"},"canary reduction exact keys drift");req(value["schema"]=="grid2d-one-two-target-gating-gpu-v3-reduction-v1" and value["mode"]=="inventory","canary schema/mode drift")
 audit=value["audit"];req(isinstance(audit,dict) and set(audit)=={"pass","fail_closed","campaign_kind","manifest_schema","manifest_filename","manifest_sha256","field_pack_filename","field_pack_sha256","source_filename","source_sha256","cell_count","inventory_digest","sacct"},"canary audit exact keys drift");req(audit.get("pass") is True and audit.get("fail_closed") is True and audit.get("campaign_kind")=="canary" and audit.get("manifest_schema")=="grid2d-one-two-target-gating-gpu-v3-manifest" and audit.get("manifest_filename")==manifest.name and audit.get("manifest_sha256")==CANARY_MANIFEST_SHA and audit.get("field_pack_filename")=="disorder_field_pack_v3.npz" and audit.get("field_pack_sha256")=="d7039cf68cd137729a3931f1265cad2735c67da3c436fc4f71d214f059f0e420" and audit.get("source_filename")=="gpu_gating_mc_v3.py" and audit.get("source_sha256")=="fbac49ca27dbb0210d9bf89f5eebe160b60ed01386a17d301408727f0a722156" and audit.get("cell_count")==8,"canary audit drift")
 sa=audit.get("sacct",{});req(isinstance(sa,dict) and set(sa)=={"provided","verified","receipt_filename","receipt_sha256","allocations_verified","cells_verified","cells_per_allocation","bundled_production"} and sa=={"provided":True,"verified":True,"receipt_filename":sacct.name,"receipt_sha256":sha(sacct),"allocations_verified":8,"cells_verified":8,"cells_per_allocation":1,"bundled_production":False},"canary reducer sacct claim drift")
 decision=value["inventory_decision"];req(decision=={"exact_inventory":True,"all_cells_validated":True,"sacct_verified_if_provided":True,"pass":True},"canary inventory decision drift")
 csvr=value["csv"];req(isinstance(csvr,dict) and set(csvr)=={"kind","filename","sha256","rows"} and csvr.get("kind")=="inventory" and csvr.get("filename")=="reduction.csv" and csvr.get("rows")==8 and csvr.get("sha256")==sha(rc),"canary CSV receipt drift")
 inventory=value["inventory"];inventory_keys={"cell_id","profile","json_path","json_sha256","npz_path","npz_sha256","slurm_array_job_id","slurm_array_task_id","slurm_job_id"};req(isinstance(inventory,list) and len(inventory)==8 and all(isinstance(x,dict) and set(x)==inventory_keys for x in inventory) and {x.get("cell_id") for x in inventory}==set(range(8)),"canary inventory exact schema/IDs drift")
 lines=[f"{row['cell_id']}\t{row['json_path']}\t{row['json_sha256']}\t{row['npz_path']}\t{row['npz_sha256']}\n" for row in inventory];inventory_digest=hashlib.sha256("".join(lines).encode()).hexdigest();req(audit["inventory_digest"]==inventory_digest,"canary inventory digest recomputation drift")
 sacct_replay=replay_canary_sacct(sacct,inventory);req(sacct_replay["receipt_sha256"]==sa["receipt_sha256"],"canary independent sacct hash drift")
 with rc.open(newline="",encoding="utf-8") as handle:reader=csv.DictReader(handle);csv_rows=list(reader);header=reader.fieldnames
 expected_header=["cell_id","profile","json_path","json_sha256","npz_path","npz_sha256","slurm_array_job_id","slurm_array_task_id","slurm_job_id"];req(header==expected_header and len(csv_rows)==8,"canary CSV exact header/row count drift")
 by_id={row["cell_id"]:row for row in inventory};req({int(row["cell_id"]) for row in csv_rows}==set(range(8)),"canary CSV IDs drift")
 for row in csv_rows:
  expected=by_id[int(row["cell_id"])];req(all(row[key]==("" if expected[key] is None else str(expected[key])) for key in expected_header),"canary CSV/inventory reverse bind drift")
 raw_members={x.name for x in raw.iterdir()};req(raw_members=={f"cell-{i}" for i in range(8)},"canary raw exact root drift")
 manifest_value=strict_json(manifest);req(manifest_value.get("schema")=="grid2d-one-two-target-gating-gpu-v3-manifest" and manifest_value.get("campaign",{}).get("kind")=="canary" and manifest_value.get("campaign",{}).get("cell_count")==8,"canary manifest content drift");configs={row["cell_id"]:row for row in manifest_value["cells"]};req(set(configs)==set(range(8)),"canary manifest IDs drift")
 for row in inventory:
  i=row["cell_id"];req(row.get("profile") is None and row.get("slurm_array_job_id")=="5788354" and row.get("slurm_array_task_id")==str(i) and isinstance(row.get("slurm_job_id"),str) and row["slurm_job_id"].isdigit(),"canary inventory job/task drift")
  d=raw/f"cell-{i}";expected={f"cell-{i}.json",f"cell-{i}.npz"};req({x.name for x in d.iterdir()}==expected,"canary raw member drift")
  for key,suffix in (("json","json"),("npz","npz")):
   p=d/f"cell-{i}.{suffix}";st=p.lstat();req(p.is_file() and not p.is_symlink() and st.st_nlink==1 and st.st_mode&0o777==0o600,"canary raw unsafe file");req(row[f"{key}_path"]==f"cell-{i}/cell-{i}.{suffix}" and row[f"{key}_sha256"]==sha(p),"canary raw reverse hash drift")
  replay_canary_raw(d/f"cell-{i}.json",d/f"cell-{i}.npz",manifest_value,configs[i],row)
 return {"schema":"grid2d-one-two-target-gating-v3-canary-release-h1","status":"PASS_CANARY_CONTENT","manifest_sha256":CANARY_MANIFEST_SHA,"reduction_json_sha256":sha(rj),"reduction_csv_sha256":sha(rc),"sacct_receipt_sha256":sha(sacct),"cell_count":8,"allocation_count":8,"cells_per_allocation":1,"csv_rows":8,"inventory_digest":inventory_digest,"independent_sacct":sacct_replay}
def verify(sacct_fixture:Path|None=None)->dict:
 payload=base.verify(sacct_fixture);req(set(payload)==RELEASE_KEYS-{"canary_reduction"},"base release exact key drift")
 root=base.V3_ROOT;payload["canary_reduction"]=validate_canary(root/"artifacts/data/gating_v3_canary_manifest.json",root/"artifacts/outputs/isambard_ai_v3/canary-5788353",root/"artifacts/outputs/isambard_ai_v3/reductions/canary-5788353-reduce-5788356")
 payload["schema"]="grid2d-one-two-target-gating-v3-release-for-v4-r2-h1";payload["status"]="PASS_AUTHORIZE_V4_R2_H1_HARDWARE_CANARY";req(set(payload)==RELEASE_KEYS,"h1 release exact keys drift");return payload
def commit(payload:dict)->None:
 req(not OUT.exists(),"h1 release receipt exists");OUT.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v3-h1.",dir=OUT.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(raw);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,OUT)
 finally:tmp.unlink(missing_ok=True)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--sacct-fixture",type=Path);a=p.parse_args()
 try:x=verify(a.sacct_fixture);commit(x)
 except Exception as e:print(f"FAIL-CLOSED: {e}",file=os.sys.stderr);return 2
 print(json.dumps({"status":x["status"],"sha256":sha(OUT)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

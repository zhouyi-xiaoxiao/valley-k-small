#!/usr/bin/env python3
"""Independent raw JSON/NPZ replay and authorization for v4-r2 pooling."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,tempfile
from pathlib import Path
from typing import Any
import numpy as np
import reduce_gpu_gating_v4_r2 as strict
ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
MANIFEST=ROOT/"artifacts/data/gating_v4_r2_production_manifest.json"
MANIFEST_SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-manifest";RESULT_SCHEMA="grid2d-one-two-target-gating-fixed-mean-gpu-v4-r2";REDUCTION_SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-reduction-v1"
def req(v:bool,m:str)->None:
 if not v:raise ValueError(m)
def sha(p:Path)->str:
 d=hashlib.sha256()
 with p.open("rb") as h:
  for c in iter(lambda:h.read(1<<20),b""):d.update(c)
 return d.hexdigest()
def load(p:Path)->dict:
 req(p.is_file() and not p.is_symlink() and p.lstat().st_nlink==1,f"unsafe input {p}");return json.loads(p.read_text())
def replay(run_token:str,reducer_job:str,array_job:str,reduction_sha:str)->dict[str,Any]:
 req(run_token.isdigit() and reducer_job.isdigit() and array_job.isdigit(),"job/run identities must be decimal")
 raw=ROOT/f"artifacts/outputs/isambard_ai_v4_r2/production-{run_token}";red_dir=ROOT/f"artifacts/outputs/isambard_ai_v4_r2/reduction-{run_token}-{reducer_job}";rj=red_dir/"reduction_v4_r2.json";rc=red_dir/"reduction_v4_r2.csv";sacct=red_dir/f"sacct-v4-r2-{array_job}.psv"
 tree=strict.exact_raw_tree(raw);req(sha(rj)==reduction_sha,"pinned reduction JSON SHA drift")
 manifest=load(MANIFEST);manifest_sha=sha(MANIFEST);req(manifest.get("schema")==MANIFEST_SCHEMA and len(manifest.get("cells",[]))==23040,"manifest drift");configs={x["cell_id"]:x for x in manifest["cells"]};req(set(configs)==set(range(23040)),"manifest cell IDs drift")
 reduction=load(rj);req(reduction.get("schema")==REDUCTION_SCHEMA and reduction.get("mode")=="full","reduction schema/mode drift");audit=reduction.get("audit",{});req(audit.get("pass") is True and audit.get("manifest_sha256")==manifest_sha and audit.get("cell_count")==23040,"reduction audit drift");sa=audit.get("sacct",{});req(sa.get("verified") is True and sa.get("allocations_verified")==480 and sa.get("cells_per_allocation")==48 and sa.get("full_node_gpus")==4,"reduction extended sacct drift");req(sa.get("receipt_sha256")==sha(sacct),"sacct receipt hash drift")
 inventory=reduction.get("inventory");req(isinstance(inventory,list) and len(inventory)==23040,"reduction inventory drift");inv={x.get("cell_id"):x for x in inventory};req(set(inv)==set(range(23040)),"inventory IDs drift")
 with rc.open(newline="",encoding="utf-8") as h:reader=csv.DictReader(h);rows=list(reader)
 req(reduction.get("csv",{}).get("sha256")==sha(rc) and reduction.get("csv",{}).get("rows")==len(rows)==11648,"reduction CSV hash/count drift")
 block_rows=[x for x in rows if x.get("row_type")=="block_mean"];primary_rows=[x for x in rows if x.get("row_type")=="primary_pair"];req(len(block_rows)==11520 and len(primary_rows)==128,"reduction CSV row types drift")
 csv_blocks={}
 for row in block_rows:
  key=(int(row["target2_x"]),int(row["target2_y"]),float(row["amplitude"]),int(row["disorder_replicate"]));req(key not in csv_blocks and row["walk_replicates"]=="0;1","CSV block duplicate/stream drift");csv_blocks[key]=float(row["gating_probability_drop"])
 streams={};raw_lines=[]
 expected_npz={"schema_version","one_target1_fpt_histogram","two_target1_fpt_histogram","two_target2_fpt_histogram","checkpoint_steps","checkpoint_counts","paired_outcome_counts"}
 for cell in range(23040):
  config=configs[cell];entry=inv[cell];jp=raw/f"cell-{cell}/cell-{cell}.json";npz=raw/f"cell-{cell}/cell-{cell}.npz";jsha,nsha=sha(jp),sha(npz)
  req(entry.get("json_path")==f"cell-{cell}/cell-{cell}.json" and entry.get("npz_path")==f"cell-{cell}/cell-{cell}.npz" and entry.get("json_sha256")==jsha and entry.get("npz_sha256")==nsha,"inventory/raw hash/path drift")
  req(entry.get("slurm_array_job_id")==array_job and entry.get("slurm_array_task_id")==str(cell%480),"inventory array mapping drift")
  payload=load(jp);req(payload.get("schema")==RESULT_SCHEMA,"raw result schema drift");mb=payload.get("manifest",{});req(mb.get("sha256")==manifest_sha and mb.get("cell_id")==cell,"raw manifest identity drift")
  params=payload.get("parameters",{});req(params.get("disorder_replicate")==config["disorder_replicate"] and params.get("walk_replicate")==config["walk_replicate"] and params.get("amplitude")==config["amplitude"],"raw parameter drift");req(payload.get("rng",{}).get("walk_seed")==config["walk_seed"],"raw walk seed drift");req(payload.get("provenance",{}).get("slurm",{}).get("SLURM_ARRAY_TASK_ID")==str(cell%480),"raw Slurm task drift");req(payload.get("gates",{}).get("all_passed") is True,"raw gates failed");req(payload.get("histograms",{}).get("sha256")==nsha,"raw JSON/NPZ hash drift")
  with np.load(npz,allow_pickle=False) as z:
   req(set(z.files)==expected_npz,"NPZ exact keys drift");one=np.asarray(z["one_target1_fpt_histogram"]);two=np.asarray(z["two_target1_fpt_histogram"]);pair=np.asarray(z["paired_outcome_counts"]);check=np.asarray(z["checkpoint_counts"]);schema=np.asarray(z["schema_version"])
  req(all(x.dtype==np.int64 for x in (one,two,pair,check,schema)) and int(schema)==3,"NPZ dtype/schema drift");walkers=1_000_000;one_hits=int(one.sum());two_hits=int(two.sum());req(int(pair.sum())==walkers and one_hits==int(pair[1,:].sum()) and two_hits==int(pair[:,1].sum()),"NPZ paired mass drift");metric=(one_hits-two_hits)/walkers;req(payload.get("gating_probability_drop")==metric,"raw metric replay drift")
  key=(config["target2_x"],config["target2_y"],config["amplitude"],config["disorder_replicate"]);by=streams.setdefault(key,{});walk=config["walk_replicate"];req(walk not in by,"duplicate raw stream");by[walk]=metric;raw_lines.append(f"{cell}\t{jsha}\t{nsha}\n")
 blocks={}
 for key,by in streams.items():req(set(by)=={0,1},"raw stream pair drift");blocks[key]=math.fsum((by[0],by[1]))/2
 req(len(blocks)==11520 and set(blocks)==set(csv_blocks),"raw/reduction block inventory drift")
 for key,value in blocks.items():req(math.isclose(value,csv_blocks[key],rel_tol=0,abs_tol=1e-15),f"raw/reduction block value drift {key}")
 block_digest=hashlib.sha256("".join(f"{x}\t{y}\t{a.hex()}\t{b}\t{v.hex()}\n" for (x,y,a,b),v in sorted(blocks.items())).encode()).hexdigest()
 return {"schema":"grid2d-one-two-target-gating-v4-r2-independent-replay-v1","status":"PASS_AUTHORIZE_V3_V4_R2_COMBINED","fixed_root":str(ROOT),"jobs":{"array":array_job,"reducer":reducer_job,"run_token":run_token},"hashes":{"manifest":manifest_sha,"reduction_json":sha(rj),"reduction_csv":sha(rc),"sacct_receipt":sha(sacct)},"raw":{"exact_tree":tree,"raw_inventory_digest":hashlib.sha256("".join(raw_lines).encode()).hexdigest(),"recomputed_block_digest":block_digest,"cells":23040,"pairs":23040,"blocks":11520},"reduction_inventory_digest":audit.get("inventory_digest"),"extended_sacct":sa}
def commit(path:Path,payload:dict)->None:
 req(not path.exists(),"replay receipt exists");path.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v4r2-replay.",dir=path.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,path)
 finally:tmp.unlink(missing_ok=True)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--run-token",required=True);p.add_argument("--array-job",required=True);p.add_argument("--reducer-job",required=True);p.add_argument("--reduction-sha256",required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 try:x=replay(a.run_token,a.reducer_job,a.array_job,a.reduction_sha256);commit(a.output,x)
 except (ValueError,OSError,json.JSONDecodeError) as e:print(f"FAIL-CLOSED: {e}",file=os.sys.stderr);return 2
 print(json.dumps({"status":x["status"],"output":str(a.output)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

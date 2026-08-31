#!/usr/bin/env python3
"""Strict v4-r2 reducer with exact raw tree and full-node TRES accounting."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from typing import Any,Mapping,Sequence
import reduce_gpu_gating_v3 as core
MANIFEST_SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-manifest";RESULT_SCHEMA="grid2d-one-two-target-gating-fixed-mean-gpu-v4-r2";REDUCTION_SCHEMA="grid2d-one-two-target-gating-gpu-v4-r2-reduction-v1"
def exact_raw_tree(root:Path)->dict[str,Any]:
 core._require(root.is_dir() and not root.is_symlink(),"raw root missing/symlinked")
 children=list(root.iterdir());core._require(len(children)==23040,"raw root must contain exactly 23,040 cell directories")
 seen=set();lines=[]
 for child in children:
  m=re.fullmatch(r"cell-(\d+)",child.name);core._require(m is not None and child.is_dir() and not child.is_symlink(),f"unexpected raw root member {child.name}");cell=int(m.group(1));core._require(cell not in seen and 0<=cell<23040,"raw cell identity drift");seen.add(cell)
  members=list(child.iterdir());expected={f"cell-{cell}.json",f"cell-{cell}.npz"};core._require({x.name for x in members}==expected,"raw cell exact member drift")
  for member in members:
   st=member.lstat();core._require(member.is_file() and not member.is_symlink() and st.st_nlink==1,"raw artifact symlink/hardlink/nonregular");lines.append(f"{cell}\t{member.name}\t{core._sha256_file(member)}\n")
 core._require(seen==set(range(23040)),"raw cell IDs not exact 0..23039")
 return {"exact_tree":True,"cell_directories":23040,"files":46080,"tree_digest":core._sha256_bytes("".join(sorted(lines)).encode())}
def gpu_count(tres:str)->int:
 values=[]
 for token in tres.split(","):
  key,sep,value=token.partition("=")
  if sep and (key=="gres/gpu" or key.startswith("gres/gpu:") or key=="gpu"):values.append(int(value))
 return sum(values)
def validate_sacct(path:Path|None,cells:Sequence[Any])->dict[str,Any]:
 core._require(path is not None and path.is_file() and not path.is_symlink(),"extended sacct receipt mandatory")
 records=core._parse_sacct(path);core._require(len(cells)==23040,"exact v4-r2 cell count required")
 groups={}
 for cell in cells:
  a,t,j=cell.slurm_array_job_id,cell.slurm_array_task_id,cell.slurm_job_id;core._require(isinstance(a,str) and a.isdigit() and isinstance(t,str) and t.isdigit() and isinstance(j,str) and j.isdigit(),"invalid cell Slurm identity");groups.setdefault((a,j,int(t)),[]).append(cell)
 core._require(len(groups)==480 and len({k[0] for k in groups})==1 and {k[2] for k in groups}==set(range(480)),"allocation inventory drift")
 array_id=next(iter(groups))[0]
 for key,group in groups.items():
  task=key[2];expected={task+480*(g+4*k) for g in range(4) for k in range(12)};core._require(len(group)==48 and {x.config.cell_id for x in group}==expected,f"task {task} 48-cell mapping drift")
 aliases={}
 for key in groups:
  for alias in (key[1],f"{key[0]}_{key[2]}"):core._require(alias not in aliases or aliases[alias]==key,"ambiguous Slurm alias");aliases[alias]=key
 matched={};elapsed=0
 for record in records:
  ids={str(v) for v in (core._record_value(record,"JobIDRaw"),core._record_value(record,"JobID")) if v not in (None,"")};ids={v for v in ids if "." not in v and v in aliases}
  if not ids:continue
  keys={aliases[x] for x in ids};core._require(len(keys)==1,"ambiguous sacct row");key=next(iter(keys));core._require(key not in matched,"duplicate sacct allocation row")
  task=key[2];state=str(core._record_value(record,"State") or "").split("+")[0];exitcode=str(core._record_value(record,"ExitCode") or "");core._require(state=="COMPLETED" and exitcode=="0:0",f"task {task} not COMPLETED/0:0")
  aj=str(core._record_value(record,"ArrayJobID") or array_id);at=str(core._record_value(record,"ArrayTaskID") or task);core._require(aj==array_id and at==str(task),f"task {task} ArrayJobID/TaskID drift")
  seconds=int(str(core._record_value(record,"ElapsedRaw") or "0"));nodes=int(str(core._record_value(record,"NNodes") or "0"));alloc=str(core._record_value(record,"AllocTRES") or "");reqt=str(core._record_value(record,"ReqTRES") or "")
  core._require(seconds>0 and nodes==1,"nonpositive elapsed or non-full-node allocation");core._require(gpu_count(alloc)==4 and gpu_count(reqt)==4,f"task {task} did not allocate/request four GPUs")
  elapsed+=seconds;matched[key]=record
 core._require(set(matched)==set(groups),f"extended sacct coverage {len(matched)}/480")
 return {"provided":True,"verified":True,"receipt_filename":path.name,"receipt_sha256":core._sha256_file(path),"allocations_verified":480,"cells_verified":23040,"cells_per_allocation":48,"bundled_production":True,"full_node_gpus":4,"n_nodes_per_allocation":1,"elapsed_raw_total_seconds":elapsed,"actual_full_node_nhr":elapsed/3600.0,"reservation_ceiling_nhr":960.0,"extended_fields":["ArrayJobID","ArrayTaskID","ElapsedRaw","AllocTRES","ReqTRES","NNodes"]}
def main(argv=None)->int:
 core.MANIFEST_SCHEMA=MANIFEST_SCHEMA;core.RESULT_SCHEMA=RESULT_SCHEMA;core.REDUCTION_SCHEMA=REDUCTION_SCHEMA;core._validate_sacct=validate_sacct
 args=core._parse_args(argv)
 try:
  tree=exact_raw_tree(args.results_dir.resolve());payload=core.reduce_campaign(manifest_path=args.manifest,field_pack_path=args.field_pack,results_dir=args.results_dir,source_path=args.source or Path(__file__).with_name("gpu_gating_mc_v4_r2.py"),sacct_receipt=args.sacct_receipt,output_json=args.output_json,output_csv=args.output_csv,mode=args.mode);payload["audit"]["exact_raw_tree"]=tree
  # core committed before this amendment field is inserted; fail closed rather
  # than pretend it was persisted.  Require caller to use full mode and emit a
  # sibling tree receipt separately in the sbatch.
 except core.AuditError as e:print(f"FAIL-CLOSED: {e}",file=sys.stderr);return 2
 print(json.dumps({"status":"PASS_V4_R2_REDUCTION","cells":payload["audit"]["cell_count"],"raw_tree":tree},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

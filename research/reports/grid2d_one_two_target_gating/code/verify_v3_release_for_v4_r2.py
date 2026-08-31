#!/usr/bin/env python3
"""Independently authorize the fixed real v3 evidence for v4-r2 release."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,subprocess,tempfile
from pathlib import Path
from typing import Any
import numpy as np
import analyze_gpu_gating_v3_secondary_r1 as secondary

V3_ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
SECONDARY_ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727")
R2_ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727")
V3_MANIFEST_SHA="419bee7e19a862a74d7ffb0072e1dc2ce3ff714335b4273003834733d77f245f"
SECONDARY_CONTRACT_SHA="96a42bd4af0260a45876ba3cae8b671bc83888cb34d89c3f9a80c99a1fb21f74"
SECONDARY_PAYLOAD_SHA="acdae65da56e5e7ff2d4de4cf36fe680ec9d5184ed211f7c726b18358d6d5c20"
V3_ACTIVE_PAYLOAD_SHA="9a56344f23afc0f14a269c7e4c10a062e920d5393032a223eccbb9eaa4269dd9"
SUBMISSION_STATE_SHA="bfdab79ad8156de7a79a3d4a475eff6608bb08354847c5036b0dc081c795b947"
JOBS=("5788353","5788354","5788356","5788357","5788358","5789031")

def req(v:bool,m:str)->None:
 if not v:raise secondary.AuditError(m)
def sha(p:Path)->str:return secondary._sha256_file(p)
def fixed_paths()->dict[str,Path]:
 reduction=V3_ROOT/"artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358"
 result=SECONDARY_ROOT/"artifacts/outputs/isambard_ai_v3/secondary_r1/upstream-5788358-secondary-5789031"
 return {"manifest":V3_ROOT/"artifacts/data/gating_v3_production_manifest.json","active_v3_payload":V3_ROOT/"notes/isambard_ai_v3_payload.sha256","submission_state":V3_ROOT/"artifacts/outputs/isambard_ai_v3/submission/submission_state_v3.json","raw":V3_ROOT/"artifacts/outputs/isambard_ai_v3/production-5788353","reduction_json":reduction/"reduction.json","reduction_csv":reduction/"reduction.csv","sacct_receipt":reduction/"sacct-production-5788353.psv","contract":SECONDARY_ROOT/"notes/isambard_ai_v3_secondary_analysis_contract_r1.json","payload":SECONDARY_ROOT/"notes/isambard_ai_v3_secondary_r1.sha256","secondary_json":result/"secondary_max_t_r1.json","secondary_csv":result/"secondary_max_t_r1.csv"}
def live_sacct(path:Path|None)->tuple[str,list[dict[str,str]]]:
 if path is None:
  cp=subprocess.run(["sacct","-X","--array","-j",",".join(JOBS),"--format=JobIDRaw,JobID,State,ExitCode","--parsable2"],check=True,capture_output=True,text=True);raw=cp.stdout
 else:req(path.is_file() and not path.is_symlink(),"live sacct fixture invalid");raw=path.read_text()
 rows=list(csv.DictReader(raw.splitlines(),delimiter="|"));req(rows and set((rows[0] if rows else {}))>={"JobIDRaw","JobID","State","ExitCode"},"live sacct header drift")
 for job in JOBS:
  matches=[r for r in rows if r.get("JobIDRaw")==job or r.get("JobID")==job]
  req(len(matches)==1,f"live sacct missing/duplicate fixed job {job}");r=matches[0];req(str(r.get("State","")).split("+")[0]=="COMPLETED" and r.get("ExitCode")=="0:0",f"fixed job {job} not COMPLETED/0:0")
 return hashlib.sha256(raw.encode()).hexdigest(),rows
def verify(sacct_fixture:Path|None=None)->dict[str,Any]:
 p=fixed_paths()
 for name,path in p.items():req(path.exists() and not path.is_symlink(),f"fixed {name} missing/symlinked")
 req(p["raw"].is_dir(),"fixed raw root not directory")
 req(sha(p["manifest"])==V3_MANIFEST_SHA,"fixed v3 manifest SHA drift")
 req(sha(p["active_v3_payload"])==V3_ACTIVE_PAYLOAD_SHA,"active v3 payload manifest SHA drift")
 for line in p["active_v3_payload"].read_text().splitlines():
  digest,relative=line.split("  ",1);member=V3_ROOT/relative;req(member.is_file() and not member.is_symlink() and sha(member)==digest,f"active v3 payload member drift: {relative}")
 req(sha(p["submission_state"])==SUBMISSION_STATE_SHA,"v3 submission state SHA drift")
 state=secondary._load_json(p["submission_state"],"v3 submission state");req(state.get("schema")=="grid2d-one-two-target-gating-isambard-submission-state-v3" and state.get("state_version")==3,"submission state schema/version drift")
 expected_chain={"environment":("5788353",None),"canary_array":("5788354","5788353"),"canary_reducer":("5788356","5788354"),"production_array":("5788357","5788356"),"production_reducer":("5788358","5788357")}
 for stage,(job,dependency) in expected_chain.items():
  entry=state.get("jobs",{}).get(stage,{});req(entry.get("job_id")==job and entry.get("dependency_afterok")==dependency,f"submission chain drift: {stage}");argv=entry.get("argv");req(isinstance(argv,list) and argv[:2]==["sbatch","--parsable"],f"submission argv drift: {stage}")
 req(sha(p["contract"])==SECONDARY_CONTRACT_SHA,"secondary contract SHA drift")
 req(sha(p["payload"])==SECONDARY_PAYLOAD_SHA,"secondary payload manifest SHA drift")
 contract=secondary._load_json(p["contract"],"fixed secondary contract");fixed=secondary._fixed_contract(contract);upstream=secondary._mapping(fixed["upstream"],"upstream")
 req(upstream["production_array_job_id"]=="5788357" and upstream["production_reducer_job_id"]=="5788358","contract job drift")
 secondary._validate_payload_manifest(p["payload"],SECONDARY_PAYLOAD_SHA)
 configs=secondary._validate_manifest(p["manifest"],fixed)
 values,input_hashes,inventory=secondary._validate_reduction(p["reduction_json"],p["reduction_csv"],p["sacct_receipt"],fixed)
 raw_values,raw_audit=secondary._independent_raw_replay(raw_root=p["raw"],configs=configs,inventory_by_id=inventory,upstream=upstream)
 req(set(raw_values)==set(values),"v3 raw/reducer key drift")
 for key,value in raw_values.items():req(math.isclose(value,values[key],rel_tol=0,abs_tol=1e-15),f"v3 raw/reducer value drift {key}")
 result=secondary._load_json(p["secondary_json"],"fixed secondary result")
 result_dir=p["secondary_json"].parent;req({x.name for x in result_dir.iterdir()}=={"secondary_max_t_r1.json","secondary_max_t_r1.csv"},"secondary output exact inventory drift")
 for path in (p["secondary_json"],p["secondary_csv"]):
  st=path.lstat();req(st.st_nlink==1 and st.st_mode&0o777==0o600,"secondary output mode/hardlink drift")
 req(result.get("schema")==secondary.OUTPUT_SCHEMA and result.get("status")=="PASS_SECONDARY_MAX_T_R1","secondary result schema/status drift")
 audit=secondary._mapping(result.get("audit"),"secondary audit");req(audit.get("pass") is True and audit.get("fail_closed") is True,"secondary audit did not pass")
 for key,value in input_hashes.items():
  req(audit.get(key)==value,f"secondary audit binding drift: {key}")
 req(audit.get("independent_raw_replay")==raw_audit,"secondary raw replay receipt drift")
 req(audit.get("contract_sha256")==SECONDARY_CONTRACT_SHA and audit.get("payload_manifest_sha256")==SECONDARY_PAYLOAD_SHA and audit.get("manifest_sha256")==V3_MANIFEST_SHA,"secondary fixed input hash drift")
 req(result.get("csv",{}).get("sha256")==sha(p["secondary_csv"]) and result.get("csv",{}).get("rows")==75,"secondary CSV receipt drift")
 columns=[(x,y,a) for x,y in fixed["geometries"] for a in fixed["treatments"]];effects=np.empty((32,75))
 for j,(x,y,a) in enumerate(columns):
  for b in range(32):effects[b,j]=values[(x,y,a,b)]-values[(x,y,0.,b)]
 means,se,t,critical,padj=secondary._max_t(effects,seed=20260726,resamples=10000,critical_index=9500)
 expected=[]
 for i,(x,y,a) in enumerate(columns):expected.append({"contrast_index":i,"target2_x":x,"target2_y":y,"control_amplitude":0.0,"treatment_amplitude":a,"n_disorder_blocks":32,"mean_effect":float(means[i]),"standard_error":float(se[i]),"observed_t":float(t[i]),"simultaneous_ci_lower":float(means[i]-critical*se[i]),"simultaneous_ci_upper":float(means[i]+critical*se[i]),"adjusted_p_value":float(padj[i])})
 req(result.get("contrasts")==expected,"secondary statistical result replay drift")
 sacct_live_sha,_=live_sacct(sacct_fixture)
 hashes={name:sha(path) for name,path in p.items() if path.is_file()}
 return {"schema":"grid2d-one-two-target-gating-v3-release-for-v4-r2-v1","status":"PASS_AUTHORIZE_V4_R2_HARDWARE_CANARY","fixed_roots":{"v3":str(V3_ROOT),"secondary":str(SECONDARY_ROOT),"v4_r2":str(R2_ROOT)},"fixed_jobs":{"environment":"5788353","canary_array":"5788354","canary_reducer":"5788356","production_array":"5788357","reducer":"5788358","secondary":"5789031"},"fixed_contracts":{"v3_manifest_sha256":V3_MANIFEST_SHA,"active_v3_payload_manifest_sha256":V3_ACTIVE_PAYLOAD_SHA,"submission_state_sha256":SUBMISSION_STATE_SHA,"secondary_contract_sha256":SECONDARY_CONTRACT_SHA,"secondary_payload_manifest_sha256":SECONDARY_PAYLOAD_SHA},"evidence_hashes":hashes,"inventory_digest":input_hashes["inventory_digest"],"raw_replay":raw_audit,"live_sacct_query_sha256":sacct_live_sha,"secondary_result_schema":result["schema"],"secondary_result_status":result["status"]}
def commit(path:Path,payload:dict)->None:
 if path.exists():raise FileExistsError("release receipt is append-only")
 path.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();fd,name=tempfile.mkstemp(prefix=".v3-release.",dir=path.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,path)
 finally:tmp.unlink(missing_ok=True)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--sacct-fixture",type=Path);a=p.parse_args()
 if a.output.absolute()!=(R2_ROOT/"artifacts/releases/v3-release-for-v4-r2.json").absolute():print("FAIL-CLOSED: output path is not fixed r2 release receipt",file=os.sys.stderr);return 2
 try:payload=verify(a.sacct_fixture);commit(a.output,payload)
 except (secondary.AuditError,ValueError,OSError,subprocess.CalledProcessError) as e:print(f"FAIL-CLOSED: {e}",file=os.sys.stderr);return 2
 print(json.dumps({"status":payload["status"],"output":str(a.output)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

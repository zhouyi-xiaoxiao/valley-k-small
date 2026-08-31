#!/usr/bin/env python3
"""Receipt-authorized v4-only and pooled 160-block preregistered inference."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,os,tempfile
from pathlib import Path
from typing import Any,Mapping
import numpy as np
from scipy.stats import t as student_t
ROOT=Path("/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727");V3=Path("/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3")
V3_RECEIPT=ROOT/"artifacts/releases/v3-release-for-v4-r2.json";GEOMETRIES=tuple((x,y) for x in (24,32,40) for y in (9,16,24,31,38));TREATMENTS=(.05,.1,.15,.2,.25);COLUMNS=tuple((x,y,a) for x,y in GEOMETRIES for a in TREATMENTS)
def req(v:bool,m:str)->None:
 if not v:raise ValueError(m)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def safe_json(p:Path)->dict:
 st=p.lstat();req(p.is_file() and not p.is_symlink() and st.st_nlink==1 and st.st_mode&0o777==0o600,f"unsafe receipt {p}");return json.loads(p.read_text())
def csv_values(path:Path,blocks:int,expected_sha:str)->dict[tuple[int,int,float,int],float]:
 req(path.is_file() and not path.is_symlink() and sha(path)==expected_sha,"authorized reduction CSV hash drift")
 with path.open(newline="",encoding="utf-8") as h:rows=list(csv.DictReader(h))
 req(len(rows)==15*6*blocks+blocks,"authorized CSV row count drift");values={};primary=0
 for row in rows:
  if row.get("row_type")=="primary_pair":primary+=1;continue
  req(row.get("row_type")=="block_mean" and row.get("walk_replicates")=="0;1","CSV row/stream drift");key=(int(row["target2_x"]),int(row["target2_y"]),float(row["amplitude"]),int(row["disorder_replicate"]));req(key not in values,"duplicate block");value=float(row["gating_probability_drop"]);req(math.isfinite(value),"nonfinite block");values[key]=value
 expected={(x,y,a,b) for x,y in GEOMETRIES for a in (0.,*TREATMENTS) for b in range(blocks)};req(set(values)==expected and primary==blocks,"CSV scientific inventory drift");return values
def effects(values:Mapping[tuple[int,int,float,int],float],blocks:int)->np.ndarray:
 a=np.empty((blocks,75))
 for j,(x,y,t) in enumerate(COLUMNS):
  for b in range(blocks):a[b,j]=values[(x,y,t,b)]-values[(x,y,0.,b)]
 return a
def decision(low:float,high:float)->str:
 if high<-.002:return "negative_change"
 if low>.002:return "positive_change"
 if low>=-.002 and high<=.002:return "practical_equivalence"
 return "inconclusive"
def primary(a:np.ndarray,label:str)->dict[str,Any]:
 index=COLUMNS.index((32,24,.2));v=a[:,index];n=len(v);mean=float(v.mean());sd=float(v.std(ddof=1));se=sd/math.sqrt(n);critical=float(student_t.ppf(.975,n-1));low,high=mean-critical*se,mean+critical*se
 return {"label":label,"geometry":{"target2_x":32,"target2_y":24},"contrast":{"high":.2,"low":0.,"direction":"high-low"},"n":n,"degrees_of_freedom":n-1,"mean":mean,"standard_deviation":sd,"standard_error":se,"t_critical":critical,"ci_lower":low,"ci_upper":high,"rope":{"lower":-.002,"upper":.002},"decision":decision(low,high)}
def max_t(a:np.ndarray,seed:int)->dict[str,Any]:
 n=a.shape[0];resamples=20000;means=a.mean(0);se=a.std(0,ddof=1)/math.sqrt(n);req(bool(np.all(se>0)),"zero observed SE");obs=means/se;rng=np.random.Generator(np.random.PCG64(seed));maxima=np.empty(resamples)
 for start in range(0,resamples,125):
  stop=min(start+125,resamples);idx=rng.integers(0,n,size=(stop-start,n),dtype=np.int64);sample=a[idx];sse=sample.std(1,ddof=1)/math.sqrt(n);req(bool(np.all(sse>0)),"zero bootstrap SE");maxima[start:stop]=np.max(np.abs((sample.mean(1)-means)/sse),axis=1)
 critical=float(np.sort(maxima)[19000]);padj=(1+np.sum(maxima[:,None]>=np.abs(obs)[None,:],axis=0))/20001
 rows=[]
 for i,(x,y,t) in enumerate(COLUMNS):rows.append({"contrast_index":i,"target2_x":x,"target2_y":y,"control_amplitude":0.,"treatment_amplitude":t,"n_disorder_blocks":n,"mean_effect":float(means[i]),"standard_error":float(se[i]),"observed_t":float(obs[i]),"simultaneous_ci_lower":float(means[i]-critical*se[i]),"simultaneous_ci_upper":float(means[i]+critical*se[i]),"adjusted_p_value":float(padj[i])})
 return {"blocks":n,"bit_generator":"PCG64","seed":seed,"resamples":resamples,"critical_order_statistic_one_indexed":19001,"critical_value":critical,"rows":rows}
def analyze(v3_sha:str,replay_path:Path,replay_sha:str)->dict[str,Any]:
 req(sha(V3_RECEIPT)==v3_sha,"fixed v3 release receipt SHA drift");v3=safe_json(V3_RECEIPT);req(v3.get("schema")=="grid2d-one-two-target-gating-v3-release-for-v4-r2-v1" and v3.get("status")=="PASS_AUTHORIZE_V4_R2_HARDWARE_CANARY","v3 release receipt not authorized")
 req(replay_path.resolve().is_relative_to((ROOT/"artifacts/replay").resolve()),"v4 replay receipt outside fixed root");req(sha(replay_path)==replay_sha,"v4 replay receipt SHA drift");v4=safe_json(replay_path);req(v4.get("schema")=="grid2d-one-two-target-gating-v4-r2-independent-replay-v1" and v4.get("status")=="PASS_AUTHORIZE_V3_V4_R2_COMBINED" and v4.get("fixed_root")==str(ROOT),"v4 replay receipt not authorized")
 v3csv=V3/"artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358/reduction.csv";req(v3["evidence_hashes"]["reduction_csv"]==sha(v3csv),"v3 release reverse hash drift")
 jobs=v4["jobs"];v4csv=ROOT/f"artifacts/outputs/isambard_ai_v4_r2/reduction-{jobs['run_token']}-{jobs['reducer']}/reduction_v4_r2.csv";req(v4["hashes"]["reduction_csv"]==sha(v4csv),"v4 replay reverse hash drift")
 a3=effects(csv_values(v3csv,32,v3["evidence_hashes"]["reduction_csv"]),32);a4=effects(csv_values(v4csv,128,v4["hashes"]["reduction_csv"]),128);pooled=np.vstack((a3,a4));req(pooled.shape==(160,75),"pooled shape drift")
 return {"schema":"grid2d-one-two-target-gating-v4-r2-combined-v1","status":"PASS_V4_R2_COMBINED_INFERENCE","authorization":{"v3_release_receipt_sha256":v3_sha,"v4_replay_receipt_sha256":replay_sha,"v3_reduction_csv_sha256":sha(v3csv),"v4_reduction_csv_sha256":sha(v4csv)},"primary":{"v4_only":primary(a4,"v4-only reflect pack"),"combined":primary(pooled,"v3 plus independent v4-r2 reflect packs")},"surface":{"v4_only":max_t(a4,2026072700),"combined":max_t(pooled,2026072701)}}
def commit(path:Path,data:bytes)->None:
 req(not path.exists(),"output exists");path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(prefix=".combined.",dir=path.parent);tmp=Path(name)
 try:
  with os.fdopen(fd,"wb") as h:h.write(data);h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o600);os.link(tmp,path)
 finally:tmp.unlink(missing_ok=True)
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--v3-release-sha256",required=True);p.add_argument("--v4-replay-receipt",type=Path,required=True);p.add_argument("--v4-replay-sha256",required=True);p.add_argument("--output-json",type=Path,required=True);p.add_argument("--output-csv",type=Path,required=True);a=p.parse_args()
 try:
  x=analyze(a.v3_release_sha256,a.v4_replay_receipt,a.v4_replay_sha256);buf=io.StringIO(newline="");w=csv.DictWriter(buf,fieldnames=tuple(x["surface"]["combined"]["rows"][0]),lineterminator="\n");w.writeheader();w.writerows(x["surface"]["combined"]["rows"]);csvdata=buf.getvalue().encode();x["csv"]={"filename":a.output_csv.name,"sha256":hashlib.sha256(csvdata).hexdigest(),"rows":75};jsondata=(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+"\n").encode();commit(a.output_csv,csvdata)
  try:commit(a.output_json,jsondata)
  except BaseException:a.output_csv.unlink(missing_ok=True);raise
 except (ValueError,OSError,json.JSONDecodeError) as e:print(f"FAIL-CLOSED: {e}",file=os.sys.stderr);return 2
 print(json.dumps({"status":x["status"],"combined_n":x["primary"]["combined"]["n"],"df":x["primary"]["combined"]["degrees_of_freedom"]},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

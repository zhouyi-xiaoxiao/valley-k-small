#!/usr/bin/env python3
"""Externally pinned H9 submit/finalize controller; deliberately not a payload member."""
from __future__ import annotations
import argparse,base64,hashlib,json,os,re,stat,subprocess,tempfile
from pathlib import Path

H9_SHA="a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA="bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN="notes/isambard_ai_v4_r2_h9_payload.sha256"
RUNTIME="code/h9_runtime_v4_r2.py"
SCRIPTS={
 "v3_authority":"code/isambard_ai_gating_v4_r2_v3_authority_h4.sbatch",
 "canary":"code/isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch",
 "production":"code/isambard_ai_gating_v4_r2_fullnode_h4.sbatch",
 "reducer":"code/isambard_ai_gating_v4_r2_reduce_h4.sbatch",
 "replay":"code/isambard_ai_gating_v4_r2_replay_h4.sbatch",
 "combined":"code/isambard_ai_gating_v4_r2_combined_h4.sbatch",
 "release":"code/isambard_ai_gating_v4_r2_release_h5.sbatch",
 "terminal":"code/isambard_ai_gating_v4_r2_terminal_h9.sbatch",
 "selftest_upstream":"code/isambard_ai_gating_v4_r2_selftest_h9.sbatch",
 "selftest_downstream":"code/isambard_ai_gating_v4_r2_selftest_h9.sbatch",
}
ORDER=("v3_authority","canary","production","reducer","replay","combined","release","terminal")
HEX=re.compile(r"[0-9a-f]{64}")
SAFE_ABS=re.compile(r"/[A-Za-z0-9._/-]+")
def req(x,msg):
 if not x: raise ValueError(msg)
def sha_bytes(x): return hashlib.sha256(x).hexdigest()
def sha(p): return sha_bytes(Path(p).read_bytes())
def safe_rel(n):
 p=Path(n); req(not p.is_absolute() and '..' not in p.parts and p.as_posix()==n,'unsafe member'); return p
def trusted_absolute(path:Path,must_exist:bool)->Path:
 p=path.absolute(); req(SAFE_ABS.fullmatch(str(p)) is not None,'unsafe absolute path quoting'); probe=p if p.exists() else p.parent
 if must_exist: req(p.exists(),'root missing')
 while True:
  req(not probe.is_symlink(),'ancestor symlink')
  if probe==probe.parent: break
  probe=probe.parent
 return p
def verify_package(root:Path)->dict[str,str]:
 req(HEX.fullmatch(H9_SHA) is not None,'controller H9 pin unset'); root=trusted_absolute(root,True); req(root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.lstat().st_mode)==0o700,'package root mode')
 m=root/MAN; req(m.is_file() and not m.is_symlink() and sha(m)==H9_SHA,'externally pinned H9 root drift'); rows={}
 for line in m.read_text().splitlines():
  z=re.fullmatch(r'([0-9a-f]{64})  ([^\x00\r\n]+)',line); req(z is not None,'manifest syntax'); d,n=z.groups(); safe_rel(n); req(n not in rows,'duplicate member'); rows[n]=d
 expected=set(rows)|{MAN}; actual=set()
 for cur,ds,fs in os.walk(root,followlinks=False):
  for d in ds:
   p=Path(cur)/d; req(not p.is_symlink() and stat.S_IMODE(p.lstat().st_mode)==0o700,'directory inventory')
  for f in fs:
   p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'file inventory'); actual.add(p.relative_to(root).as_posix())
 req(actual==expected,'closed inventory drift')
 for n,d in rows.items(): req(sha(root/n)==d,f'member drift {n}')
 req(sha(root/'notes/isambard_ai_v4_r2_h8_payload.sha256')==H8_SHA and sha(root/'notes/isambard_ai_v4_r2_h7_payload.sha256')==H7_SHA,'parent anchors')
 return rows
def exact_file(root:Path,name:str,rows:dict[str,str])->bytes:
 req(name in rows,'captured source absent from manifest'); p=root/name; before=p.lstat(); data=p.read_bytes(); after=p.lstat()
 req(stat.S_ISREG(before.st_mode) and not p.is_symlink() and before.st_ino==after.st_ino and before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns and sha_bytes(data)==rows[name],'captured source TOCTOU/hash drift')
 return data
def parse_inputs(run:Path,values:list[str])->list[dict]:
 result=[]
 for value in values:
  req('=' in value,'phase input syntax'); name,d=value.rsplit('=',1); safe_rel(name); req(name.startswith('artifacts/') and HEX.fullmatch(d) is not None,'phase input value')
  p=run/name; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and sha(p)==d,'phase input drift'); result.append({'path':name,'sha256':d})
 req(len(result)==len({x['path'] for x in result}),'duplicate phase input'); return result
def render(package:Path,run:Path,phase:str,args:list[str],inputs:list[dict],rows:dict[str,str])->bytes:
 science=exact_file(package,SCRIPTS[phase],rows); runtime=exact_file(package,RUNTIME,rows); text=science.decode(); directives=[]
 for line in text.splitlines()[1:]:
  if line.startswith('#SBATCH') and not any(x in line for x in ('--chdir','--output','--error')): directives.append(line)
 config={'schema':'h9-runtime-config-v1','phase':'production' if phase=='production' else phase,'package_root':str(package),'run_root':str(run),'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'science_path':SCRIPTS[phase],'science_sha256':sha_bytes(science),'science_bytes_hex':science.hex(),'phase_args':args,'phase_inputs':inputs}
 rb64=base64.b64encode(runtime).decode(); cb64=base64.b64encode(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).decode()
 lines=['#!/usr/bin/env bash',*directives,f'#SBATCH --chdir={run}',f'#SBATCH --output={run}/logs/%x-%A_%a.out',f'#SBATCH --error={run}/logs/%x-%A_%a.err','set -euo pipefail','umask 077','[[ -n "${SLURM_TMPDIR:-}" ]] || exit 90','launch="$(mktemp -d "$SLURM_TMPDIR/h9-launch.XXXXXX")"','trap \'rm -rf "$launch"\' EXIT',f"printf %s {rb64} | base64 -d > \"$launch/runtime.py\"",f"printf %s {cb64} | base64 -d > \"$launch/config.json\"",'chmod 400 "$launch/runtime.py" "$launch/config.json"','python3 "$launch/runtime.py" --config "$launch/config.json"']
 return ('\n'.join(lines)+'\n').encode()
def receipt(run:Path,phase:str,job:str)->Path: return run/'artifacts/h9_receipts'/f'{phase}-{job}.json'
def load_json600(path:Path)->dict:
 s=path.lstat(); req(stat.S_ISREG(s.st_mode) and not path.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'unsafe receipt'); return json.loads(path.read_text())
def validate_submission(path:Path,phase:str,job:str,run:Path)->dict:
 v=load_json600(path); req(v.get('schema')=='h9-submission-receipt-v1' and v.get('status')=='SUBMITTED_EXACT_VERIFIED_STDIN_BYTES' and v.get('phase')==phase and v.get('job_id')==job,'submission receipt identity')
 req((v.get('h9'),v.get('h8'),v.get('h7'))==(H9_SHA,H8_SHA,H7_SHA) and v.get('run_root')==str(run) and v.get('package_root'),'submission root anchors')
 script=run/safe_rel(v.get('submitted_script_path','')); s=script.lstat(); req(stat.S_ISREG(s.st_mode) and not script.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and sha(script)==v.get('submitted_script_sha256'),'submitted stdin byte archive drift')
 req(v.get('stdin_submission') is True and v.get('authorizes_scientific_release') is False,'submission authority drift'); return v
def validate_runtime(v:dict,phase:str,submission:dict,run:Path,array_job:str|None=None,task:int|None=None)->None:
 req(v.get('schema')=='h9-runtime-receipt-v1' and v.get('status')=='PASS_H9_RUNTIME_EXECUTED_FROM_JOB_PRIVATE_SNAPSHOT' and v.get('phase')==phase,'runtime receipt status')
 req((v.get('h9'),v.get('h8'),v.get('h7'))==(H9_SHA,H8_SHA,H7_SHA) and v.get('submitted_script_sha256')==submission['submitted_script_sha256'],'runtime anchor/script binding')
 req(v.get('package_root')==submission['package_root'] and v.get('run_root')==str(run) and v.get('science_source',{}).get('path')==submission['science_path'] and v.get('science_source',{}).get('sha256')==submission['science_sha256'],'runtime roots/science binding')
 req(v.get('phase_inputs')==submission['phase_inputs'] and v.get('phase_args_sha256')==sha_bytes(json.dumps(submission['phase_args'],separators=(',',':'),ensure_ascii=True).encode()),'runtime phase input/argv binding')
 outputs=v.get('outputs'); req(isinstance(outputs,list) and len(outputs)==len({x.get('path') for x in outputs if isinstance(x,dict)}),'runtime output schema')
 for item in outputs:
  req(set(item)=={'path','sha256'} and HEX.fullmatch(item['sha256']) is not None,'runtime output record'); p=run/safe_rel(item['path']); s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and sha(p)==item['sha256'],'runtime output drift')
 if task is not None: req(v.get('slurm_array_job_id')==array_job and v.get('slurm_array_task_id')==task,'array receipt identity')
def completed_sacct(sacct:str,job:str)->dict:
 raw=subprocess.run([sacct,'-X','-j',job,'-n','-P','-o','JobIDRaw,State,ExitCode,ElapsedRaw'],capture_output=True,check=True).stdout.decode(); return parse_sacct(raw,job)
def completed_array_sacct(sacct:str,job:str)->dict:
 raw=subprocess.run([sacct,'-X','--array','-j',job,'-n','-P','-o','JobIDRaw,JobID,ArrayJobID,ArrayTaskID,State,ExitCode,ElapsedRaw'],capture_output=True,check=True).stdout.decode(); return parse_array_sacct(raw,job)
def exact_production_tasks(values:list[int])->None:
 req(len(values)==len(set(values)) and set(values)==set(range(480)),'production task-index set drift')
def prior_gate(run:Path,phase:str,dependency:str,sacct:str)->None:
 idx=ORDER.index(phase); req(idx>0 and dependency.isdecimal(),'dependency gate'); previous=ORDER[idx-1]
 submissions=run/'artifacts/h9_submissions'; matches=list(submissions.glob(f'{previous}-{dependency}.json')); req(len(matches)==1,'missing upstream submission'); sub=validate_submission(matches[0],previous,dependency,run)
 if previous=='production':
  paths=list((run/'artifacts/h9_receipts').glob(f'production-{dependency}_*.json')); seen={}
  for p in paths:
   v=load_json600(p); task=v.get('slurm_array_task_id'); req(isinstance(task,int) and task not in seen,'duplicate array task receipt'); validate_runtime(v,'production',sub,run,dependency,task); seen[task]=p
  exact_production_tasks(list(seen)); completed_array_sacct(sacct,dependency)
 else: validate_runtime(load_json600(receipt(run,previous,dependency)),previous,sub,run)
 if previous!='production': completed_sacct(sacct,dependency)
def submit(package:Path,run:Path,phase:str,args:list[str],input_values:list[str],dependency:str|None,sbatch:str='sbatch',scontrol:str='scontrol',sacct:str='sacct')->dict:
 req(phase in SCRIPTS and phase not in ('selftest_downstream',) or phase=='selftest_downstream','phase')
 package=trusted_absolute(package,True); run=trusted_absolute(run,False); req(package!=run and package not in run.parents and run not in package.parents,'root separation/quoting')
 rows=verify_package(package); run.mkdir(parents=True,exist_ok=True,mode=0o700); (run/'logs').mkdir(exist_ok=True,mode=0o700)
 if phase in ORDER and ORDER.index(phase)>0: req(dependency is not None,'missing dependency'); prior_gate(run,phase,dependency,sacct)
 if phase=='selftest_downstream': req(dependency is not None,'missing selftest dependency'); sub=validate_submission(run/'artifacts/h9_submissions'/f'selftest_upstream-{dependency}.json','selftest_upstream',dependency,run); validate_runtime(load_json600(receipt(run,'selftest_upstream',dependency)),'selftest_upstream',sub,run); completed_sacct(sacct,dependency)
 inputs=parse_inputs(run,input_values); data=render(package,run,phase,args,inputs,rows); script_sha=sha_bytes(data); verify_package(package); req(sha_bytes(exact_file(package,SCRIPTS[phase],rows))==rows[SCRIPTS[phase]],'post-render captured source drift')
 export=f'ALL,H9_SUBMITTED_SCRIPT_SHA256={script_sha},H9_PAYLOAD_SHA256={H9_SHA},H8_PAYLOAD_SHA256={H8_SHA},H7_PAYLOAD_SHA256={H7_SHA}'
 cmd=[sbatch,'--parsable',f'--chdir={run}',f'--export={export}']+([f'--dependency=afterok:{dependency}'] if dependency else [])
 cp=subprocess.run(cmd,input=data,capture_output=True,check=False); req(cp.returncode==0,f'sbatch failed: {cp.stderr.decode(errors="replace")[:1000]}'); job=cp.stdout.decode().strip().split(';')[0]; req(job.isdecimal(),'sbatch job id')
 readback=subprocess.run([scontrol,'show','job','-o',job],capture_output=True,check=True).stdout.decode().strip(); expected_dep=f'Dependency=afterok:{dependency}' if dependency else 'Dependency=(null)'
 req(f'JobId={job}' in readback and f'WorkDir={run}' in readback and expected_dep in readback and ('Command=(null)' in readback or '/slurm_script' in readback) and 'StdIn=/dev/null' in readback,'scontrol stdin/dependency/workdir drift')
 d=run/'artifacts/h9_submissions'; d.mkdir(parents=True,exist_ok=True,mode=0o700); archive=d/f'{phase}-{job}.sbatch'; req(not archive.exists(),'submitted byte archive collision'); archive.write_bytes(data); os.chmod(archive,0o600)
 value={'schema':'h9-submission-receipt-v1','status':'SUBMITTED_EXACT_VERIFIED_STDIN_BYTES','phase':phase,'job_id':job,'dependency_afterok':dependency,'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'package_root':str(package),'run_root':str(run),'science_path':SCRIPTS[phase],'science_sha256':rows[SCRIPTS[phase]],'submitted_script_path':str(archive.relative_to(run)),'submitted_script_sha256':script_sha,'phase_args':args,'phase_inputs':inputs,'argv':cmd,'scontrol_readback':readback,'stdin_submission':True,'authorizes_scientific_release':False}
 out=d/f'{phase}-{job}.json'; req(not out.exists(),'submission receipt collision'); out.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n'); os.chmod(out,0o600); return value
def parse_sacct(text:str,expected:str)->dict:
 rows=[x for x in text.splitlines() if x]; req(len(rows)==1,'terminal sacct cardinality'); parts=rows[0].split('|'); req(len(parts)>=4 and parts[0]==expected and parts[1]=='COMPLETED' and parts[2]=='0:0','terminal sacct state'); return {'job_id_raw':parts[0],'state':parts[1],'exit_code':parts[2],'elapsed_raw':parts[3]}
def parse_array_sacct(text:str,array_job:str)->dict:
 rows=[x.split('|') for x in text.splitlines() if x]; seen={}
 for p in rows:
  req(len(p)>=7 and p[2]==array_job and p[3].isdecimal() and p[4]=='COMPLETED' and p[5]=='0:0','array terminal sacct row'); task=int(p[3]); req(task not in seen,'duplicate array sacct task'); seen[task]={'job_id_raw':p[0],'job_id':p[1],'array_job_id':p[2],'array_task_id':task,'state':p[4],'exit_code':p[5],'elapsed_raw':p[6]}
 req(set(seen)==set(range(480)),'array terminal sacct task set'); return {'array_job_id':array_job,'tasks':[seen[i] for i in range(480)]}
def finalize(run:Path,jobs:dict,sacct:str='sacct')->dict:
 req(set(jobs)==set(ORDER) and all(str(v).isdecimal() for v in jobs.values()) and len(set(map(str,jobs.values())))==len(ORDER),'final job set'); receipts=[]; accounting=[]; previous=None
 for phase in ORDER:
  job=str(jobs[phase]); sub=validate_submission(run/'artifacts/h9_submissions'/f'{phase}-{job}.json',phase,job,run)
  req(sub.get('dependency_afterok')==previous,'final dependency chain'); expected='Dependency=(null)' if previous is None else f'Dependency=afterok:{previous}'; req(expected in sub.get('scontrol_readback',''),'final scontrol dependency replay')
  if phase=='production':
   for task in range(480):
    v=load_json600(run/'artifacts/h9_receipts'/f'production-{job}_{task}.json'); validate_runtime(v,phase,sub,run,job,task); receipts.append({'path':f'artifacts/h9_receipts/production-{job}_{task}.json','sha256':sha(run/f'artifacts/h9_receipts/production-{job}_{task}.json')})
  else:
   p=receipt(run,phase,job); validate_runtime(load_json600(p),phase,sub,run); receipts.append({'path':str(p.relative_to(run)),'sha256':sha(p)})
  if phase=='production':
   raw=subprocess.run([sacct,'-X','--array','-j',job,'-n','-P','-o','JobIDRaw,JobID,ArrayJobID,ArrayTaskID,State,ExitCode,ElapsedRaw'],capture_output=True,check=True).stdout.decode(); accounting.append(parse_array_sacct(raw,job))
  else:
   raw=subprocess.run([sacct,'-X','-j',job,'-n','-P','-o','JobIDRaw,State,ExitCode,ElapsedRaw'],capture_output=True,check=True).stdout.decode(); accounting.append(parse_sacct(raw,job))
  previous=job
 value={'schema':'grid2d-v4-r2-h9-terminal-candidate-v1','status':'PASS_H9_REPLAYED_TERMINAL_CANDIDATE_NO_SCIENTIFIC_AUTHORITY','h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'jobs':jobs,'runtime_receipts':receipts,'terminal_sacct':accounting,'highest_root_authority':'H9','authorizes_execution':False,'authorizes_scientific_release':False}
 out=run/'artifacts/h9_final/terminal-candidate.json'; out.parent.mkdir(parents=True,exist_ok=True,mode=0o700); req(not out.exists(),'H9 final collision'); out.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n'); os.chmod(out,0o600); return value
def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True); s=sub.add_parser('submit'); s.add_argument('--package-root',type=Path,required=True); s.add_argument('--run-root',type=Path,required=True); s.add_argument('--phase',choices=SCRIPTS,required=True); s.add_argument('--dependency'); s.add_argument('--phase-input',action='append',default=[]); s.add_argument('stage_args',nargs='*'); f=sub.add_parser('finalize'); f.add_argument('--run-root',type=Path,required=True); f.add_argument('--jobs-json',required=True); a=p.parse_args()
 print(json.dumps(submit(a.package_root,a.run_root,a.phase,a.stage_args,a.phase_input,a.dependency) if a.command=='submit' else finalize(a.run_root,json.loads(a.jobs_json)),sort_keys=True)); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except (ValueError,OSError,json.JSONDecodeError,subprocess.CalledProcessError) as e: print(f'FAIL-CLOSED: {e}',file=os.sys.stderr); raise SystemExit(2)

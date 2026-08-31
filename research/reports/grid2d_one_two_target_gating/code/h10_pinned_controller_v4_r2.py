#!/usr/bin/env python3
"""Externally pinned H10 intent/recovery, live-accounting, and final controller."""
from __future__ import annotations
import argparse,base64,hashlib,json,os,re,stat,subprocess
from pathlib import Path

H10_SHA="__H10_PIN_PENDING__"; H9_SHA="a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"; H8_SHA="bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"; H7_SHA="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN="notes/isambard_ai_v4_r2_h10_payload.sha256"; RUNTIME="code/h10_runtime_v4_r2.py"; ZERO="0"*64
SCRIPTS={"v3_authority":"code/isambard_ai_gating_v4_r2_v3_authority_h4.sbatch","canary":"code/isambard_ai_gating_v4_r2_gpu_canary_h4.sbatch","production":"code/isambard_ai_gating_v4_r2_fullnode_h4.sbatch","reducer":"code/isambard_ai_gating_v4_r2_reduce_h4.sbatch","replay":"code/isambard_ai_gating_v4_r2_replay_h4.sbatch","combined":"code/isambard_ai_gating_v4_r2_combined_h4.sbatch","release":"code/isambard_ai_gating_v4_r2_release_h5.sbatch","terminal":"code/isambard_ai_gating_v4_r2_terminal_h9.sbatch","selftest_upstream":"code/isambard_ai_gating_v4_r2_selftest_h9.sbatch","selftest_downstream":"code/isambard_ai_gating_v4_r2_selftest_h9.sbatch"}
ORDER=("v3_authority","canary","production","reducer","replay","combined","release","terminal"); HEX=re.compile(r"[0-9a-f]{64}"); SAFE_ABS=re.compile(r"/[A-Za-z0-9._/-]+")
def req(x,msg):
 if not x: raise ValueError(msg)
def sha_bytes(x): return hashlib.sha256(x).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def canonical_sha(v): return sha_bytes(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def safe_rel(n):
 p=Path(n); req(isinstance(n,str) and n not in ('','.') and not p.is_absolute() and '..' not in p.parts and p.as_posix()==n,'unsafe relative'); return p
def trusted_abs(p,must=True):
 p=Path(p).absolute(); req(SAFE_ABS.fullmatch(str(p)) is not None,'unsafe absolute path'); q=p if p.exists() else p.parent
 if must: req(p.exists(),'missing path')
 while True:
  req(not q.is_symlink(),'ancestor symlink')
  if q==q.parent: break
  q=q.parent
 return p
def exclusive(path,data,mode=0o600):
 raw=data if isinstance(data,bytes) else (json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode(); path.parent.mkdir(parents=True,exist_ok=True,mode=0o700); fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 try: os.write(fd,raw); os.fsync(fd)
 finally: os.close(fd)
 return sha_bytes(raw)
def json600(path):
 s=path.lstat(); req(stat.S_ISREG(s.st_mode) and not path.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'unsafe JSON receipt'); return json.loads(path.read_text())
def verify_package(root):
 req(HEX.fullmatch(H10_SHA) is not None,'H10 pin unset'); root=trusted_abs(root); req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode)==0o700,'root mode'); m=root/MAN; req(sha(m)==H10_SHA,'externally pinned H10 drift'); rows={}
 for line in m.read_text().splitlines():
  z=re.fullmatch(r'([0-9a-f]{64})  ([^\x00\r\n]+)',line); req(z is not None,'manifest syntax'); d,n=z.groups(); safe_rel(n); req(n not in rows,'duplicate member'); rows[n]=d
 actual=set()
 for cur,ds,fs in os.walk(root,followlinks=False):
  for d in ds:
   p=Path(cur)/d; req(not p.is_symlink() and stat.S_IMODE(p.lstat().st_mode)==0o700,'directory inventory')
  for f in fs:
   p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'file inventory'); actual.add(p.relative_to(root).as_posix())
 req(actual==set(rows)|{MAN},'closed inventory')
 for n,d in rows.items(): req(sha(root/n)==d,f'member drift {n}')
 req(sha(root/'notes/isambard_ai_v4_r2_h9_payload.sha256')==H9_SHA and sha(root/'notes/isambard_ai_v4_r2_h8_payload.sha256')==H8_SHA and sha(root/'notes/isambard_ai_v4_r2_h7_payload.sha256')==H7_SHA,'parent pins'); return rows
def capture(root,n,rows):
 req(n in rows,'source outside manifest'); p=root/n; a=p.lstat(); data=p.read_bytes(); b=p.lstat(); req(a.st_ino==b.st_ino and a.st_mtime_ns==b.st_mtime_ns and a.st_size==b.st_size and sha_bytes(data)==rows[n],'captured bytes TOCTOU'); return data
def phase_inputs(run,values):
 out=[]
 for v in values:
  req('=' in v,'input syntax'); n,d=v.rsplit('=',1); safe_rel(n); req(n.startswith('artifacts/') and HEX.fullmatch(d) is not None,'input shape'); p=run/n; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and sha(p)==d,'input drift'); out.append({'path':n,'sha256':d})
 req(len(out)==len({x['path'] for x in out}),'duplicate input'); return out
def render(package,run,phase,args,inputs,rows):
 science=capture(package,SCRIPTS[phase],rows); runtime=capture(package,RUNTIME,rows); directives=[]
 for line in science.decode().splitlines()[1:]:
  if line.startswith('#SBATCH') and not any(x in line for x in ('--chdir','--output','--error')): directives.append(line)
 config={'schema':'h10-runtime-config-v1','phase':'production' if phase=='production' else phase,'package_root':str(package),'run_root':str(run),'h10':H10_SHA,'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'science_path':SCRIPTS[phase],'science_sha256':sha_bytes(science),'science_bytes_hex':science.hex(),'phase_args':args,'phase_inputs':inputs}
 rb64=base64.b64encode(runtime).decode(); cb64=base64.b64encode(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).decode()
 lines=['#!/usr/bin/env bash',*directives,f'#SBATCH --chdir={run}',f'#SBATCH --output={run}/logs/%x-%A_%a.out',f'#SBATCH --error={run}/logs/%x-%A_%a.err','set -euo pipefail','umask 077',f'export H10_EXPECTED_BINDING_SHA256={ZERO}','export H10_SUBMITTED_SCRIPT_PATH="$0"','[[ -n "${SLURM_TMPDIR:-}" ]] || exit 90','launch="$(mktemp -d "$SLURM_TMPDIR/h10-launch.XXXXXX")"','trap \'rm -rf "$launch"\' EXIT',f'printf %s {rb64} | base64 -d > "$launch/runtime.py"',f'printf %s {cb64} | base64 -d > "$launch/config.json"','chmod 400 "$launch/runtime.py" "$launch/config.json"','python3 "$launch/runtime.py" --config "$launch/config.json"']
 template=('\n'.join(lines)+'\n').encode(); binding=sha_bytes(template); final=template.replace(f'H10_EXPECTED_BINDING_SHA256={ZERO}'.encode(),f'H10_EXPECTED_BINDING_SHA256={binding}'.encode()); req(final!=template,'binding insertion'); return final,binding,sha_bytes(final)
def intent_paths(run,phase,intent):
 d=run/'artifacts/h10_intents'; return d/f'{phase}-{intent}.json',d/f'{phase}-{intent}.sbatch',d/f'{phase}-{intent}.dispatch.json',d/f'{phase}-{intent}.job.json'
def squeue_jobs(squeue,intent):
 argv=[squeue,'-h','-o','%i|%k|%T']; raw=subprocess.run(argv,capture_output=True,check=True).stdout.decode(); rows=[]
 for line in raw.splitlines():
  if not line: continue
  p=line.split('|'); req(len(p)==3,'squeue shape')
  if p[1]==f'H10:{intent}': req(p[0].isdecimal(),'squeue job'); rows.append({'job_id':p[0],'comment':p[1],'state':p[2]})
 return argv,raw,rows
def show(scontrol,job): return subprocess.run([scontrol,'show','job','-o',job],capture_output=True,check=True).stdout.decode().strip()
def submission_path(run,phase,job): return run/'artifacts/h10_submissions'/f'{phase}-{job}.json'
def release_path(run,phase,job): return run/'artifacts/h10_releases'/f'{phase}-{job}.json'
def recover_intent(run,phase,intent,squeue='squeue',scontrol='scontrol',known_job=None):
 ip,archive,dispatch,jobclaim=intent_paths(run,phase,intent); iv=json600(ip); req(canonical_sha({k:v for k,v in iv.items() if k!='sbatch_argv'})==intent and iv['phase']==phase and iv['status']=='PREPARED_HELD_SUBMISSION_INTENT_AUTHORITY_FALSE','intent binding'); req(sha(archive)==iv['submitted_script_sha256'],'intent archive drift'); argv,raw,jobs=squeue_jobs(squeue,intent)
 if known_job is None and jobclaim.exists(): known_job=str(json600(jobclaim)['job_id'])
 if known_job is not None:
  req(known_job.isdecimal(),'known job'); rb=show(scontrol,known_job); req(f'Comment=H10:{intent}' in rb,'known job comment'); jobs=[{'job_id':known_job,'comment':f'H10:{intent}','state':'UNKNOWN'}]
 req(len(jobs)==1,'intent recovery requires exactly one job'); job=jobs[0]['job_id']; pre=show(scontrol,job); req(f'JobId={job}' in pre and f'Comment=H10:{intent}' in pre and f'WorkDir={run}' in pre and any(x in pre for x in ('JobState=PENDING','JobState=RUNNING','JobState=COMPLETED','Reason=JobHeldUser')),'scontrol recovery readback')
 sp=submission_path(run,phase,job); sub={'schema':'h10-submission-receipt-v1','status':'RECOVERED_UNIQUE_HELD_JOB_EXACT_STDIN','phase':phase,'job_id':job,'intent_sha256':intent,'h10':H10_SHA,'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'package_root':iv['package_root'],'run_root':str(run),'dependency_afterok':iv['dependency_afterok'],'science_path':iv['science_path'],'science_sha256':iv['science_sha256'],'submitted_script_path':str(archive.relative_to(run)),'submitted_script_sha256':iv['submitted_script_sha256'],'submitted_script_binding_sha256':iv['submitted_script_binding_sha256'],'phase_args':iv['phase_args'],'phase_inputs':iv['phase_inputs'],'sbatch_argv':iv['sbatch_argv'],'squeue_recovery':{'argv':argv,'raw_stdout_sha256':sha_bytes(raw.encode()),'matched_job':job},'held_scontrol_readback':pre,'authorizes_scientific_release':False}
 if not sp.exists(): exclusive(sp,sub)
 else: req(json600(sp)==sub,'submission recovery drift')
 rp=release_path(run,phase,job)
 if not rp.exists():
  held='Reason=JobHeldUser' in pre; release_argv=[scontrol,'release',job] if held else []; cp=subprocess.run(release_argv,capture_output=True,check=True) if held else None; post=show(scontrol,job); rel={'schema':'h10-release-receipt-v1','status':'RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT' if held else 'RECOVERED_ALREADY_RELEASED_AFTER_DURABLE_SUBMISSION_RECEIPT','phase':phase,'job_id':job,'intent_sha256':intent,'submission_receipt_sha256':sha(sp),'argv':release_argv,'stdout_sha256':sha_bytes(cp.stdout) if cp else sha_bytes(b''),'post_release_scontrol':post,'h10':H10_SHA,'authorizes_scientific_release':False}
  if os.environ.get('H10_TEST_CRASH_AFTER_RELEASE')=='1': raise RuntimeError('H10 injected post-release crash')
  exclusive(rp,rel)
 return {'submission':json600(sp),'release':json600(rp) if rp.exists() else None}
def submit(package,run,phase,args,input_values,dependency=None,sbatch='sbatch',squeue='squeue',scontrol='scontrol',sacct='sacct'):
 req(phase in SCRIPTS,'phase'); package=trusted_abs(package); run=trusted_abs(run,False); req(package!=run and package not in run.parents and run not in package.parents,'roots mixed'); rows=verify_package(package); run.mkdir(parents=True,exist_ok=True,mode=0o700); (run/'logs').mkdir(exist_ok=True,mode=0o700)
 if phase in ORDER and ORDER.index(phase)>0:
  req(dependency and dependency.isdecimal(),'missing dependency'); prior_gate(run,ORDER[ORDER.index(phase)-1],dependency,sacct)
 if phase=='selftest_downstream': req(dependency and dependency.isdecimal(),'missing selftest dependency'); prior_gate(run,'selftest_upstream',dependency,sacct)
 inputs=phase_inputs(run,input_values); data,binding,exact=render(package,run,phase,args,inputs,rows)
 base={'schema':'h10-submission-intent-v1','status':'PREPARED_HELD_SUBMISSION_INTENT_AUTHORITY_FALSE','phase':phase,'dependency_afterok':dependency,'h10':H10_SHA,'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'package_root':str(package),'run_root':str(run),'science_path':SCRIPTS[phase],'science_sha256':rows[SCRIPTS[phase]],'submitted_script_sha256':exact,'submitted_script_binding_sha256':binding,'phase_args':args,'phase_inputs':inputs,'authorizes_scientific_release':False}; intent=canonical_sha(base); comment=f'H10:{intent}'; cmd=[sbatch,'--parsable','--hold',f'--comment={comment}',f'--chdir={run}']+([f'--dependency=afterok:{dependency}'] if dependency else []); base['sbatch_argv']=cmd
 # The intent digest excludes argv only to avoid a comment self-reference; all argv except the derived comment are already represented by fields above.
 ip,archive,dispatch,jobclaim=intent_paths(run,phase,intent)
 if ip.exists(): req(json600(ip)==base and sha(archive)==exact,'existing intent drift'); return recover_intent(run,phase,intent,squeue,scontrol)
 if not archive.exists(): exclusive(archive,data)
 else: req(sha(archive)==exact,'existing intent archive drift')
 exclusive(ip,base); exclusive(dispatch,{'schema':'h10-dispatch-start-v1','intent_sha256':intent,'comment':comment,'status':'DISPATCH_UNCERTAIN_UNTIL_UNIQUE_COMMENT_READBACK'})
 cp=subprocess.run(cmd,input=data,capture_output=True,check=True); job=cp.stdout.decode().strip().split(';')[0]; req(job.isdecimal(),'sbatch job id')
 exclusive(jobclaim,{'schema':'h10-dispatch-job-claim-v1','intent_sha256':intent,'job_id':job,'comment':comment})
 if os.environ.get('H10_TEST_CRASH_AFTER_SBATCH')=='1': raise RuntimeError('H10 injected sbatch-receipt crash')
 return recover_intent(run,phase,intent,squeue,scontrol,job)
def parse_nonarray(raw,job):
 lines=[x for x in raw.splitlines() if x]; req(len(lines)==1,'nonarray sacct row count'); p=lines[0].split('|'); req(len(p)==5 and p[0]==job and p[1]==job and p[2]=='COMPLETED' and p[3]=='0:0' and p[4].isdecimal(),'nonarray live sacct shape'); return [{'job_id_raw':p[0],'job_id':p[1],'state':p[2],'exit_code':p[3],'elapsed_raw':int(p[4]),'array_job_id':None,'array_task_id':None}]
def parse_array(raw,parent):
 lines=[x for x in raw.splitlines() if x]; req(len(lines)==480,'array live sacct row count'); rows={}; rawids=set()
 for line in lines:
  p=line.split('|'); req(len(p)==5 and p[0].isdecimal() and p[2]=='COMPLETED' and p[3]=='0:0' and p[4].isdecimal(),'array live sacct field shape'); z=re.fullmatch(re.escape(parent)+r'_([0-9]+)',p[1]); req(z is not None,'array JobID shape'); task=int(z.group(1)); req(task not in rows and p[0] not in rawids,'array duplicate identity'); rawids.add(p[0]); rows[task]={'job_id_raw':p[0],'job_id':p[1],'state':p[2],'exit_code':p[3],'elapsed_raw':int(p[4]),'array_job_id':parent,'array_task_id':task}
 req(set(rows)==set(range(480)),'array exact task set'); return [rows[i] for i in range(480)]
def accounting(run,phase,job,sacct='sacct'):
 fields='JobIDRaw,JobID,State,ExitCode,ElapsedRaw'; argv=[sacct,'-X']+(['--array'] if phase=='production' else [])+['-j',job,'-n','-P','-o',fields]; raw=subprocess.run(argv,capture_output=True,check=True).stdout.decode(); rows=parse_array(raw,job) if phase=='production' else parse_nonarray(raw,job); value={'schema':'h10-accounting-receipt-v1','status':'PASS_EXACT_LIVE_SACCT_TERMINAL_BINDING','phase':phase,'parent_job_id':job,'h10':H10_SHA,'argv':argv,'raw_stdout':raw,'raw_stdout_sha256':sha_bytes(raw.encode()),'rows':rows,'authorizes_scientific_release':False}; p=run/'artifacts/h10_accounting'/f'{phase}-{job}.json'
 if not p.exists(): exclusive(p,value)
 else: req(json600(p)==value,'accounting receipt drift')
 return value,p
def validate_submission(run,phase,job):
 v=json600(submission_path(run,phase,job)); req(v['phase']==phase and v['job_id']==job and (v['h10'],v['h9'],v['h8'],v['h7'])==(H10_SHA,H9_SHA,H8_SHA,H7_SHA),'submission identity'); req(sha(run/v['submitted_script_path'])==v['submitted_script_sha256'],'submitted archive'); r=json600(release_path(run,phase,job)); req(r['submission_receipt_sha256']==sha(submission_path(run,phase,job)) and r['intent_sha256']==v['intent_sha256'],'release binding'); return v
def validate_runtime(run,phase,job,sub,acct):
 receipts=run/'artifacts/h10_receipts'; values=[]
 if phase=='production': paths=[receipts/f'production-{job}_{i}.json' for i in range(480)]
 else: paths=[receipts/f'{phase}-{job}.json']
 for i,p in enumerate(paths):
  v=json600(p); row=acct['rows'][i]; req(v['schema']=='h10-runtime-receipt-v1' and v['phase']==phase and (v['h10'],v['h9'],v['h8'],v['h7'])==(H10_SHA,H9_SHA,H8_SHA,H7_SHA),'runtime schema/anchors'); req(v['submitted_script_sha256']==sub['submitted_script_sha256'] and v['submitted_script_binding_sha256']==sub['submitted_script_binding_sha256'],'runtime script binding'); req(v['slurm_job_id']==row['job_id_raw'] and v['slurm_array_job_id']==row['array_job_id'] and v['slurm_array_task_id']==row['array_task_id'] and v['terminal_sacct_identity']==row,'runtime live accounting identity'); req(v['phase_inputs']==sub['phase_inputs'] and v['phase_args_sha256']==sha_bytes(json.dumps(sub['phase_args'],separators=(',',':')).encode()),'runtime inputs/argv');
  for x in v['outputs']:
   q=run/safe_rel(x['path']); req(q.is_file() and not q.is_symlink() and sha(q)==x['sha256'],'runtime output drift')
  values.append((p,v))
 return values
def prior_gate(run,phase,job,sacct='sacct'):
 sub=validate_submission(run,phase,job); acct,ap=accounting(run,phase,job,sacct); values=validate_runtime(run,phase,job,sub,acct); return {'submission':sub,'accounting':acct,'accounting_path':ap,'runtime':values}
def finalize(run,jobs,sacct='sacct'):
 run=trusted_abs(run); req(set(jobs)==set(ORDER) and len(set(map(str,jobs.values())))==8,'final job set'); previous=None; phases=[]
 for phase in ORDER:
  job=str(jobs[phase]); gate=prior_gate(run,phase,job,sacct); req(gate['submission']['dependency_afterok']==previous,'dependency chain'); phases.append({'phase':phase,'job_id':job,'submission_sha256':sha(submission_path(run,phase,job)),'release_sha256':sha(release_path(run,phase,job)),'accounting_path':str(gate['accounting_path'].relative_to(run)),'accounting_sha256':sha(gate['accounting_path']),'accounting_raw_stdout_sha256':gate['accounting']['raw_stdout_sha256'],'runtime_receipts':[{'path':str(p.relative_to(run)),'sha256':sha(p)} for p,v in gate['runtime']]}); previous=job
 value={'schema':'grid2d-v4-r2-h10-terminal-candidate-v1','status':'PASS_H10_LIVE_ACCOUNTING_TRANSACTION_REPLAY_NO_AUTHORITY','h10':H10_SHA,'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'highest_root_authority':'H10','phases':phases,'authorizes_execution':False,'authorizes_scientific_release':False}; out=run/'artifacts/h10_final/terminal-candidate.json'; exclusive(out,value); return value
def main():
 p=argparse.ArgumentParser(); sp=p.add_subparsers(dest='cmd',required=True); s=sp.add_parser('submit'); s.add_argument('--package-root',type=Path,required=True); s.add_argument('--run-root',type=Path,required=True); s.add_argument('--phase',choices=SCRIPTS,required=True); s.add_argument('--dependency'); s.add_argument('--phase-input',action='append',default=[]); s.add_argument('stage_args',nargs='*'); r=sp.add_parser('recover-intent'); r.add_argument('--run-root',type=Path,required=True); r.add_argument('--phase',required=True); r.add_argument('--intent-sha256',required=True); f=sp.add_parser('finalize'); f.add_argument('--run-root',type=Path,required=True); f.add_argument('--jobs-json',required=True); a=p.parse_args(); result=submit(a.package_root,a.run_root,a.phase,a.stage_args,a.phase_input,a.dependency) if a.cmd=='submit' else recover_intent(a.run_root,a.phase,a.intent_sha256) if a.cmd=='recover-intent' else finalize(a.run_root,json.loads(a.jobs_json)); print(json.dumps(result,sort_keys=True)); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except (ValueError,OSError,json.JSONDecodeError,RuntimeError,subprocess.CalledProcessError) as e: print(f'FAIL-CLOSED: {e}',file=os.sys.stderr); raise SystemExit(2)

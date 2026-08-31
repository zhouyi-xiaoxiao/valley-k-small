#!/usr/bin/env python3
"""H10 job-private execution with recoverable transactional output export."""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,stat,subprocess,tempfile
from pathlib import Path

H9_SHA="a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa"
H8_SHA="bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a"
H7_SHA="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN="notes/isambard_ai_v4_r2_h10_payload.sha256"; H9_MAN="notes/isambard_ai_v4_r2_h9_payload.sha256"
OLD_ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727"
HEX=re.compile(r"[0-9a-f]{64}"); SAFE_ABS=re.compile(r"/[A-Za-z0-9._/-]+")
def req(x,msg):
 if not x: raise ValueError(msg)
def sha_bytes(x): return hashlib.sha256(x).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def safe_rel(n):
 p=Path(n); req(isinstance(n,str) and n not in ('','.') and not p.is_absolute() and '..' not in p.parts and p.as_posix()==n,'unsafe relative path'); return p
def trusted_abs(p,must=True):
 p=Path(p).absolute(); req(SAFE_ABS.fullmatch(str(p)) is not None,'unsafe absolute path'); q=p if p.exists() else p.parent
 if must: req(p.exists(),'missing path')
 while True:
  req(not q.is_symlink(),'ancestor symlink')
  if q==q.parent: break
  q=q.parent
 return p
def exclusive_json(path,value,mode=0o600):
 data=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode(); path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 try:
  os.write(fd,data); os.fsync(fd)
 finally: os.close(fd)
 return sha_bytes(data)
def manifest(root,anchor,file_mode=0o600,dir_mode=0o700):
 req(HEX.fullmatch(anchor) is not None,'H10 anchor shape'); root=trusted_abs(root); req(root.is_dir() and stat.S_IMODE(root.lstat().st_mode)==dir_mode,'root mode')
 m=root/MAN; req(m.is_file() and not m.is_symlink() and sha(m)==anchor,'H10 manifest pin'); rows={}
 raw=m.read_bytes(); req(raw.endswith(b'\n') and b'\r' not in raw,'manifest canonical bytes')
 for line in raw.decode().splitlines():
  z=re.fullmatch(r'([0-9a-f]{64})  ([^\x00\r\n]+)',line); req(z is not None,'manifest syntax'); d,n=z.groups(); safe_rel(n); req(n not in rows,'duplicate member'); rows[n]=d
 actual=set()
 for cur,ds,fs in os.walk(root,followlinks=False):
  for d in ds:
   p=Path(cur)/d; s=p.lstat(); req(stat.S_ISDIR(s.st_mode) and not p.is_symlink() and stat.S_IMODE(s.st_mode)==dir_mode,'directory inventory')
  for f in fs:
   p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==file_mode,'file inventory'); actual.add(p.relative_to(root).as_posix())
 req(actual==set(rows)|{MAN},'closed inventory');
 for n,d in rows.items(): req(sha(root/n)==d,f'member drift {n}')
 req(sha(root/H9_MAN)==H9_SHA and sha(root/'notes/isambard_ai_v4_r2_h8_payload.sha256')==H8_SHA and sha(root/'notes/isambard_ai_v4_r2_h7_payload.sha256')==H7_SHA,'fixed parent drift')
 return rows
def copy_snapshot(package,snapshot,h10):
 rows=manifest(package,h10); req(not snapshot.exists() and not snapshot.is_symlink(),'snapshot collision'); snapshot.mkdir(mode=0o700)
 baseline={**rows,MAN:h10}
 for n,d in baseline.items():
  t=snapshot/safe_rel(n); t.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(package/n,t); os.chmod(t,0o400); req(sha(t)==d,'snapshot copy digest')
 for cur,ds,fs in os.walk(snapshot): os.chmod(cur,0o700)
 manifest(snapshot,h10,0o400,0o700); manifest(package,h10); return baseline
def copy_inputs(run,snapshot,records,baseline):
 imported={}
 for x in records:
  req(set(x)=={'path','sha256'} and HEX.fullmatch(x['sha256']) is not None,'input schema'); n=x['path']; safe_rel(n); req(n.startswith('artifacts/') and n not in baseline and n not in imported,'input namespace/collision')
  s=run/n; st=s.lstat(); req(stat.S_ISREG(st.st_mode) and not s.is_symlink() and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600 and sha(s)==x['sha256'],'input source drift')
  t=snapshot/n; t.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(s,t); os.chmod(t,0o400); req(sha(t)==x['sha256'],'copied phase-input digest drift'); imported[n]=x['sha256']
 return imported
def inv(root):
 out={}
 for cur,ds,fs in os.walk(root,followlinks=False):
  for d in ds:
   p=Path(cur)/d; s=p.lstat(); req(stat.S_ISDIR(s.st_mode) and not p.is_symlink() and stat.S_IMODE(s.st_mode)==0o700,'runtime directory drift')
  for f in fs:
   p=Path(cur)/f; s=p.lstat(); req(stat.S_ISREG(s.st_mode) and not p.is_symlink() and s.st_nlink==1 and stat.S_IMODE(s.st_mode) in (0o400,0o600),'runtime file drift'); out[p.relative_to(root).as_posix()]={'sha256':sha(p),'mode':stat.S_IMODE(s.st_mode)}
 return out
def mapped_args(args,run,package,snapshot,imported):
 out=[]
 for v in args:
  if v.startswith(str(run)+'/'):
   n=Path(v).relative_to(run).as_posix(); req(n in imported,'argv run path not bound'); out.append(str(snapshot/n))
  else: req(not v.startswith('/') and not v.startswith(str(package)+'/'),'absolute argv snapshot bypass'); out.append(v)
 return out
def script_binding(path,expected):
 data=path.read_bytes(); actual=sha_bytes(data); normalized,count=re.subn(rb'H10_EXPECTED_BINDING_SHA256=[0-9a-f]{64}',b'H10_EXPECTED_BINDING_SHA256='+b'0'*64,data)
 req(count==1 and sha_bytes(normalized)==expected,'embedded submitted-script binding'); return actual
def receipt_name(phase,array,task,job): return f'{phase}-{array}_{task}.json' if task is not None else f'{phase}-{job}.json'
def recover_transaction(txdir,crash_after=None):
 planpath=txdir/'plan.json'; st=planpath.lstat(); req(stat.S_ISREG(st.st_mode) and not planpath.is_symlink() and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o600,'transaction plan unsafe'); plan=json.loads(planpath.read_text()); req(plan.get('schema')=='h10-output-transaction-v1' and plan.get('status')=='PREPARED_AUTHORITY_FALSE','transaction plan schema')
 run=trusted_abs(plan['run_root']); staged=txdir/'staged'; promoted=0
 for x in plan['outputs']:
  n=x['path']; safe_rel(n); s=staged/n; req(s.is_file() and not s.is_symlink() and sha(s)==x['sha256'],'staged output drift'); t=run/n; t.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  if t.exists(): req(t.is_file() and not t.is_symlink() and sha(t)==x['sha256'],'partial export collision')
  else: os.link(s,t); os.chmod(t,0o600)
  promoted+=1
  if crash_after is not None and promoted>=crash_after: raise RuntimeError('H10 injected export crash')
 complete=txdir/'complete.json'
 if not complete.exists(): exclusive_json(complete,{'schema':'h10-output-transaction-complete-v1','status':'COMMITTED_IDEMPOTENT','plan_sha256':sha(planpath),'outputs':plan['outputs']})
 rpath=run/plan['receipt_path']
 if not rpath.exists(): exclusive_json(rpath,plan['receipt'])
 else: req(sha(rpath)==sha_bytes((json.dumps(plan['receipt'],sort_keys=True,separators=(',',':'))+'\n').encode()),'recovered receipt drift')
 return plan['receipt']
def prepare_transaction(run,key,outputs,snapshot,receipt):
 tx=run/'artifacts/h10_transactions'/key; tx.mkdir(parents=True,exist_ok=False,mode=0o700); staged=tx/'staged'; staged.mkdir(mode=0o700)
 for x in outputs:
  s=snapshot/x['path']; t=staged/x['path']; t.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(s,t); os.chmod(t,0o600); req(sha(t)==x['sha256'],'transaction stage copy drift')
 plan={'schema':'h10-output-transaction-v1','status':'PREPARED_AUTHORITY_FALSE','run_root':str(run),'outputs':outputs,'receipt_path':f"artifacts/h10_receipts/{key}.json",'receipt':receipt,'authorizes_scientific_release':False}; exclusive_json(tx/'plan.json',plan); return tx
def execute(c):
 keys={'schema','phase','package_root','run_root','h10','h9','h8','h7','science_path','science_sha256','science_bytes_hex','phase_args','phase_inputs'}; req(set(c)==keys and c['schema']=='h10-runtime-config-v1','config schema'); req((c['h9'],c['h8'],c['h7'])==(H9_SHA,H8_SHA,H7_SHA),'parent anchors')
 package=trusted_abs(c['package_root']); run=trusted_abs(c['run_root']); rawtmp=os.environ.get('SLURM_TMPDIR',''); req(rawtmp.startswith('/'),'SLURM_TMPDIR'); tmp=trusted_abs(rawtmp)
 job=os.environ.get('SLURM_JOB_ID',''); array=os.environ.get('SLURM_ARRAY_JOB_ID'); taskraw=os.environ.get('SLURM_ARRAY_TASK_ID'); req(job.isdecimal(),'JobIDRaw runtime identity'); task=int(taskraw) if taskraw is not None else None
 if c['phase']=='production': req(array and array.isdecimal() and task is not None and 0<=task<480,'array runtime identity')
 else: req(array is None and task is None,'nonarray runtime identity')
 script=trusted_abs(os.environ.get('H10_SUBMITTED_SCRIPT_PATH','')); binding=os.environ.get('H10_EXPECTED_BINDING_SHA256',''); req(HEX.fullmatch(binding) is not None,'expected script binding missing'); actual_script=script_binding(script,binding)
 suffix=f'{array}_{task}' if task is not None else job; snapshot=tmp/f"h10-{c['phase']}-{suffix}"; baseline=copy_snapshot(package,snapshot,c['h10']); imported=copy_inputs(run,snapshot,c['phase_inputs'],baseline); before={**baseline,**imported}
 science=bytes.fromhex(c['science_bytes_hex']); req(sha_bytes(science)==c['science_sha256']==baseline.get(c['science_path']),'captured science binding'); body=('\n'.join(x for x in science.decode().splitlines()[1:] if not x.startswith('#SBATCH')).replace(OLD_ROOT,str(snapshot))+'\n').encode(); args=mapped_args(c['phase_args'],run,package,snapshot,imported)
 cp=subprocess.run(['bash','-s','--',*args],input=body,cwd=snapshot,env={**os.environ,'H10_PACKAGE_ROOT':str(package),'H10_RUN_ROOT':str(run),'H10_SNAPSHOT_ROOT':str(snapshot)},check=False); req(cp.returncode==0,'science body failed')
 after=inv(snapshot)
 for n,d in before.items(): req(n in after and after[n]['sha256']==d and after[n]['mode']==0o400,'immutable pre/post drift')
 new=sorted(set(after)-set(before)); req(all(n.startswith('artifacts/') for n in new),'output namespace'); outputs=[{'path':n,'sha256':after[n]['sha256']} for n in new]
 identity={'job_id_raw':job,'job_id':f'{array}_{task}' if task is not None else job,'array_job_id':array,'array_task_id':task}
 receipt={'schema':'h10-runtime-receipt-v1','status':'PASS_H10_JOB_PRIVATE_SNAPSHOT_TRANSACTION_COMMITTED','phase':c['phase'],'h10':c['h10'],'h9':H9_SHA,'h8':H8_SHA,'h7':H7_SHA,'package_root':str(package),'run_root':str(run),'slurm_job_id':job,'slurm_array_job_id':array,'slurm_array_task_id':task,'submitted_script_sha256':actual_script,'submitted_script_binding_sha256':binding,'science_source':{'path':c['science_path'],'sha256':c['science_sha256'],'derived_body_sha256':sha_bytes(body)},'phase_args_sha256':sha_bytes(json.dumps(c['phase_args'],separators=(',',':')).encode()),'effective_phase_args_sha256':sha_bytes(json.dumps(args,separators=(',',':')).encode()),'phase_inputs':c['phase_inputs'],'outputs':outputs,'terminal_sacct_identity':identity,'authorizes_scientific_release':False}
 key=receipt_name(c['phase'],array,task,job).removesuffix('.json'); tx=prepare_transaction(run,key,outputs,snapshot,receipt); crash=os.environ.get('H10_TEST_CRASH_AFTER_EXPORT'); return recover_transaction(tx,int(crash) if crash else None)
def recover_all(run):
 run=trusted_abs(run); out=[]; root=run/'artifacts/h10_transactions'
 if not root.exists(): return out
 for tx in sorted(root.iterdir()):
  if tx.is_dir() and not tx.is_symlink(): out.append(recover_transaction(tx))
 return out
def main():
 p=argparse.ArgumentParser(); p.add_argument('--config',type=Path); p.add_argument('--recover-run',type=Path); a=p.parse_args(); req((a.config is None)!=(a.recover_run is None),'choose execute or recover'); print(json.dumps(execute(json.loads(a.config.read_text())) if a.config else recover_all(a.recover_run),sort_keys=True)); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except (ValueError,OSError,json.JSONDecodeError,RuntimeError) as e: print(f'FAIL-CLOSED: {e}',file=os.sys.stderr); raise SystemExit(2)

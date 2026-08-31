#!/usr/bin/env python3
"""H10 live-format, intent-recovery, script-binding and export-transaction tests."""
from __future__ import annotations
import json,os,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import build_isambard_ai_v4_r2_h10_payload as build
import h10_runtime_v4_r2 as runtime
import h10_pinned_controller_v4_r2 as controller

class H10Tests(unittest.TestCase):
 def deploy(self,base):
  root=base/'package'; root.mkdir(mode=0o700)
  for n in (*build.MEMBERS,runtime.MAN):
   t=root/n; t.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(build.ROOT/n,t); os.chmod(t,0o600)
  for cur,ds,fs in os.walk(root): os.chmod(cur,0o700)
  return root
 def test_frozen_h7_h8_h9(self):
  self.assertEqual(build.h9.verify(),build.H9_SHA); self.assertEqual(runtime.H9_SHA,build.H9_SHA); self.assertEqual(controller.H8_SHA,runtime.H8_SHA); self.assertEqual(controller.H7_SHA,runtime.H7_SHA)
 def test_append_only_h9_prefix(self): self.assertEqual(build.MEMBERS[:len(build.h9.MEMBERS)],build.h9.MEMBERS)
 def test_live_array_fixture_exact_480(self):
  raw=(build.ROOT/'notes/isambard_ai_v4_r2_h10_sacct_live_array_fixture.psv').read_text(); rows=controller.parse_array(raw,'9000000'); self.assertEqual(len(rows),480); self.assertEqual(rows[37]['job_id'],'9000000_37'); self.assertEqual(rows[37]['job_id_raw'],'9100037')
 def test_live_nonarray_fixture(self):
  raw=(build.ROOT/'notes/isambard_ai_v4_r2_h10_sacct_live_nonarray_fixture.psv').read_text(); self.assertEqual(controller.parse_nonarray(raw,'9200000')[0]['job_id_raw'],'9200000')
 def test_unsupported_h9_fields_absent(self):
  text=Path(controller.__file__).read_text(); self.assertNotIn("'ArrayJobID,ArrayTaskID'",text); self.assertIn("fields='JobIDRaw,JobID,State,ExitCode,ElapsedRaw'",text)
 def test_array_missing_duplicate_bad_jobid_rejected(self):
  raw=(build.ROOT/'notes/isambard_ai_v4_r2_h10_sacct_live_array_fixture.psv').read_text(); lines=raw.splitlines()
  with self.assertRaisesRegex(ValueError,'row count'): controller.parse_array('\n'.join(lines[:-1])+'\n','9000000')
  with self.assertRaisesRegex(ValueError,'duplicate'): controller.parse_array('\n'.join(lines[:-1]+[lines[0]])+'\n','9000000')
  bad=lines.copy(); bad[2]=bad[2].replace('9000000_2','9000001_2')
  with self.assertRaisesRegex(ValueError,'JobID shape'): controller.parse_array('\n'.join(bad)+'\n','9000000')
 def test_script_binding_is_embedded_not_export_trusted(self):
  text=Path(controller.__file__).read_text(); self.assertIn('H10_EXPECTED_BINDING_SHA256=',text); self.assertNotIn('H10_SUBMITTED_SCRIPT_SHA256=',text)
 def test_transaction_crash_recovery_idempotent(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td).resolve(); run=base/'run'; snap=base/'snap'; run.mkdir(mode=0o700); snap.mkdir(mode=0o700); outputs=[]
   for i in range(2):
    n=f'artifacts/out/f{i}.txt'; p=snap/n; p.parent.mkdir(parents=True,exist_ok=True,mode=0o700); p.write_text(f'{i}\n'); os.chmod(p,0o600); outputs.append({'path':n,'sha256':runtime.sha(p)})
   receipt={'schema':'h10-runtime-receipt-v1','status':'test'}; tx=runtime.prepare_transaction(run,'phase-1',outputs,snap,receipt)
   with self.assertRaisesRegex(RuntimeError,'injected'): runtime.recover_transaction(tx,1)
   self.assertTrue((run/outputs[0]['path']).exists()); runtime.recover_transaction(tx); runtime.recover_transaction(tx)
   self.assertTrue((run/outputs[1]['path']).exists()); self.assertTrue((tx/'complete.json').exists()); self.assertTrue((run/'artifacts/h10_receipts/phase-1.json').exists())
 def test_ocl_exclusive_receipt(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'x.json'; runtime.exclusive_json(p,{'x':1})
   with self.assertRaises(FileExistsError): runtime.exclusive_json(p,{'x':1})
 def fake_tools(self,base):
  tools=base/'tools'; tools.mkdir(mode=0o700); state=base/'state.json'; state.write_text(json.dumps({'next':9300000,'jobs':{}})); os.chmod(state,0o600)
  sbatch=tools/'sbatch'; sbatch.write_text('''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
s=Path(os.environ["H10_FAKE_STATE"]); v=json.loads(s.read_text()); j=str(v["next"]); v["next"]+=1; args=sys.argv[1:]; comment=next(x.split("=",1)[1] for x in args if x.startswith("--comment=")); work=next(x.split("=",1)[1] for x in args if x.startswith("--chdir=")); dep=next((x.split(":",1)[1] for x in args if x.startswith("--dependency=")),None); script=s.parent/f"job-{j}.sh"; script.write_bytes(sys.stdin.buffer.read()); os.chmod(script,0o700); v["jobs"][j]={"comment":comment,"work":work,"dep":dep,"state":"PENDING","reason":"JobHeldUser","script":str(script)}; s.write_text(json.dumps(v)); print(j)
'''); os.chmod(sbatch,0o700)
  squeue=tools/'squeue'; squeue.write_text('''#!/usr/bin/env python3
import json,os
v=json.load(open(os.environ["H10_FAKE_STATE"]));
for j,x in v["jobs"].items():
 if x["state"] in ("PENDING","RUNNING"): print(f"{j}|{x['comment']}|{x['state']}")
'''); os.chmod(squeue,0o700)
  scontrol=tools/'scontrol'; scontrol.write_text('''#!/usr/bin/env python3
import json,os,subprocess,sys,tempfile
from pathlib import Path
s=Path(os.environ["H10_FAKE_STATE"]); v=json.loads(s.read_text()); cmd=sys.argv[1]; j=sys.argv[-1]; x=v["jobs"][j]
if cmd=="show":
 dep="afterok:"+x["dep"] if x["dep"] else "(null)"; print(f"JobId={j} JobState={x['state']} Reason={x['reason']} Comment={x['comment']} WorkDir={x['work']} Dependency={dep} Command=/tmp/slurm_script StdIn=/dev/null"); raise SystemExit
if cmd=="release":
 x["state"]="RUNNING"; x["reason"]="None"; s.write_text(json.dumps(v)); env=os.environ.copy(); tmp=Path(tempfile.mkdtemp(prefix="h10-fake-")).resolve(); env.update({"SLURM_JOB_ID":j,"SLURM_TMPDIR":str(tmp)}); cp=subprocess.run(["bash",x["script"]],env=env,capture_output=True); v=json.loads(s.read_text()); v["jobs"][j]["state"]="COMPLETED" if cp.returncode==0 else "FAILED"; v["jobs"][j]["reason"]="None"; s.write_text(json.dumps(v));
 if cp.returncode: sys.stderr.buffer.write(cp.stderr); raise SystemExit(cp.returncode)
 print("released",j)
'''); os.chmod(scontrol,0o700)
  sacct=tools/'sacct'; sacct.write_text('''#!/usr/bin/env python3
import sys
j=sys.argv[sys.argv.index("-j")+1]; print(f"{j}|{j}|COMPLETED|0:0|7")
'''); os.chmod(sacct,0o700)
  return state,sbatch,squeue,scontrol,sacct
 def test_fake_slurm_sbatch_receipt_crash_unique_recovery_and_chain(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td).resolve(); os.chmod(base,0o700); package=self.deploy(base); run=base/'run'; state,sbatch,squeue,scontrol,sacct=self.fake_tools(base); env={'H10_FAKE_STATE':str(state),'H9_TEST_OUTPUT_NAME':'up','H10_TEST_CRASH_AFTER_SBATCH':'1'}
   with patch.dict(os.environ,env,clear=False):
    with self.assertRaisesRegex(RuntimeError,'sbatch-receipt'): controller.submit(package,run,'selftest_upstream',['alpha','one'],[],None,str(sbatch),str(squeue),str(scontrol),str(sacct))
   intent_file=next((run/'artifacts/h10_intents').glob('selftest_upstream-*.json')); intent=intent_file.stem.split('-',1)[1]
   env.pop('H10_TEST_CRASH_AFTER_SBATCH');
   with patch.dict(os.environ,env,clear=False): recovered=controller.recover_intent(run,'selftest_upstream',intent,str(squeue),str(scontrol))
   job=recovered['submission']['job_id']; self.assertEqual(json600:=controller.json600(controller.submission_path(run,'selftest_upstream',job))['job_id'],job); self.assertEqual((run/'artifacts/h9_e2e/up.txt').read_text(),'alpha:one\n')
   env['H9_TEST_OUTPUT_NAME']='down'; inp=run/'artifacts/h9_e2e/up.txt'
   with patch.dict(os.environ,env,clear=False): down=controller.submit(package,run,'selftest_downstream',['beta','two'],[f'artifacts/h9_e2e/up.txt={runtime.sha(inp)}'],job,str(sbatch),str(squeue),str(scontrol),str(sacct))
   self.assertEqual((run/'artifacts/h9_e2e/down.txt').read_text(),'beta:two\n'); self.assertEqual(down['submission']['dependency_afterok'],job)

if __name__=='__main__': unittest.main()

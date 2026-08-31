#!/usr/bin/env python3
"""Focused H9 regressions, including a local fake-Slurm two-job chain."""
from __future__ import annotations
import json,os,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import build_isambard_ai_v4_r2_h9_payload as build
import h9_runtime_v4_r2 as runtime
import h9_pinned_controller_v4_r2 as controller

class H9Tests(unittest.TestCase):
 def deploy(self,base:Path)->Path:
  root=base/'package'; root.mkdir(mode=0o700)
  for name in (*build.MEMBERS,runtime.H9_MANIFEST):
   target=root/name; target.parent.mkdir(parents=True,exist_ok=True,mode=0o700); shutil.copyfile(build.ROOT/name,target); os.chmod(target,0o600)
  for cur,dirs,files in os.walk(root): os.chmod(cur,0o700)
  return root
 def test_parent_bytes_frozen(self):
  self.assertEqual(build.h8.verify(),build.H8_SHA); self.assertEqual(runtime.H8_SHA,build.H8_SHA); self.assertEqual(runtime.H7_SHA,controller.H7_SHA)
 def test_h9_is_append_only_h8_extension(self): self.assertEqual(build.MEMBERS[:len(build.h8.MEMBERS)],build.h8.MEMBERS)
 def test_self_rebound_manifest_rejected_by_external_pin(self):
  with tempfile.TemporaryDirectory() as td:
   root=self.deploy(Path(td).resolve()); target=root/'code/h9_runtime_v4_r2.py'; target.write_bytes(target.read_bytes()+b'\n'); os.chmod(target,0o600)
   rows=[]
   for line in (root/runtime.H9_MANIFEST).read_text().splitlines():
    d,n=line.split('  ',1); rows.append(f"{runtime.sha(root/n) if n=='code/h9_runtime_v4_r2.py' else d}  {n}")
   (root/runtime.H9_MANIFEST).write_text('\n'.join(rows)+'\n'); os.chmod(root/runtime.H9_MANIFEST,0o600)
   with self.assertRaisesRegex(ValueError,'pinned H9'): controller.verify_package(root)
 def test_traversal_rejected(self):
  with self.assertRaisesRegex(ValueError,'unsafe relative'): runtime.safe_name('../x')
 def test_direct_capture_hash_and_stdin_submission_present(self):
  text=Path(controller.__file__).read_text(); self.assertIn('sha_bytes(data)==rows[name]',text); self.assertIn('input=data',text)
 def test_runtime_uses_per_task_slurm_tmpdir(self):
  text=Path(runtime.__file__).read_text(); self.assertIn('SLURM_TMPDIR missing/nonabsolute',text); self.assertIn('suffix=f"{array}_{task}"',text)
 def test_absolute_argv_cannot_bypass_snapshot(self):
  with self.assertRaisesRegex(ValueError,'bypasses snapshot'): runtime.snapshot_args(['/tmp/unbound'],Path('/safe/run'),Path('/safe/package'),Path('/safe/snapshot'),{})
 def test_exact_480_index_gate(self):
  controller.exact_production_tasks(list(range(480)))
  with self.assertRaisesRegex(ValueError,'task-index'): controller.exact_production_tasks(list(range(479)))
  with self.assertRaisesRegex(ValueError,'task-index'): controller.exact_production_tasks(list(range(479))+[478])
 def test_receipt_binds_required_fields(self):
  text=Path(runtime.__file__).read_text()
  for key in ('submitted_script_sha256','science_source','phase_inputs','outputs','terminal_sacct_identity','slurm_array_job_id','slurm_array_task_id'): self.assertIn(key,text)
 def test_final_authority_is_h9_and_false(self):
  text=Path(controller.__file__).read_text(); self.assertIn("'highest_root_authority':'H9'",text); self.assertIn("'authorizes_scientific_release':False",text)
 def test_snapshot_source_mutation_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=self.deploy(Path(td).resolve()); anchor=build.verify(); snap=Path(td).resolve()/'snap'; runtime.copy_package(root,snap,anchor); p=snap/'code/h9_runtime_v4_r2.py'; os.chmod(p,0o600); p.write_bytes(p.read_bytes()+b'x'); os.chmod(p,0o400)
   with self.assertRaisesRegex(ValueError,'member drift'): runtime.parse_manifest(snap,anchor,file_mode=0o400,dir_mode=0o700)
 def test_captured_source_mutate_read_restore_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=self.deploy(Path(td).resolve()); rows=controller.verify_package(root); target=root/'code/isambard_ai_gating_v4_r2_selftest_h9.sbatch'; original=target.read_bytes(); st=target.stat(); real=Path.read_bytes
   def attack(path):
    if path==target:
     path.write_bytes(b'X'*len(original)); changed=real(path); path.write_bytes(original); os.utime(path,ns=(st.st_atime_ns,st.st_mtime_ns)); return changed
    return real(path)
   with patch.object(Path,'read_bytes',attack):
    with self.assertRaisesRegex(ValueError,'TOCTOU/hash'): controller.exact_file(root,'code/isambard_ai_gating_v4_r2_selftest_h9.sbatch',rows)
 def test_ancestor_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td).resolve(); real=base/'real'; real.mkdir(); link=base/'link'; link.symlink_to(real,True)
   with self.assertRaisesRegex(ValueError,'ancestor symlink'): controller.trusted_absolute(link,True)
 def test_fake_slurm_two_job_end_to_end(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td).resolve(); os.chmod(base,0o700); package=self.deploy(base); run=base/'run'; tools=base/'tools'; tools.mkdir(mode=0o700); state=base/'state.json'; state.write_text(json.dumps({'next':700,'jobs':{}})); os.chmod(state,0o600)
   sbatch=tools/'sbatch'; sbatch.write_text('''#!/usr/bin/env python3
import json,os,subprocess,sys,tempfile
from pathlib import Path
s=Path(os.environ["H9_FAKE_STATE"]); v=json.loads(s.read_text()); job=str(v["next"]); v["next"]+=1
args=sys.argv[1:]; export=next(x.split("=",1)[1] for x in args if x.startswith("--export=")); dep=next((x.split(":",1)[1] for x in args if x.startswith("--dependency=")),None); work=next(x.split("=",1)[1] for x in args if x.startswith("--chdir=")); env=os.environ.copy()
for item in export.split(",")[1:]:
 k,val=item.split("=",1); env[k]=val
tmp=Path(tempfile.mkdtemp(prefix="h9-fake-slurm-")).resolve(); env.update({"SLURM_JOB_ID":job,"SLURM_TMPDIR":str(tmp)})
cp=subprocess.run(["bash","-s"],input=sys.stdin.buffer.read(),env=env,capture_output=True)
if cp.returncode:
 sys.stderr.buffer.write(cp.stderr); raise SystemExit(cp.returncode)
v["jobs"][job]={"work":work,"dep":dep}; s.write_text(json.dumps(v)); print(job)
'''); os.chmod(sbatch,0o700)
   scontrol=tools/'scontrol'; scontrol.write_text('''#!/usr/bin/env python3
import json,os,sys
v=json.load(open(os.environ["H9_FAKE_STATE"])); j=sys.argv[-1]; x=v["jobs"][j]; dep="afterok:"+x["dep"] if x["dep"] else "(null)"; print(f"JobId={j} WorkDir={x['work']} Dependency={dep} Command=(null) StdIn=/dev/null")
'''); os.chmod(scontrol,0o700)
   sacct=tools/'sacct'; sacct.write_text('''#!/usr/bin/env python3
import sys
j=sys.argv[sys.argv.index("-j")+1]; print(f"{j}|COMPLETED|0:0|1")
'''); os.chmod(sacct,0o700)
   env={'H9_FAKE_STATE':str(state),'H9_TEST_OUTPUT_NAME':'up'}
   with patch.dict(os.environ,env,clear=False): up=controller.submit(package,run,'selftest_upstream',['alpha','one'],[],None,str(sbatch),str(scontrol),str(sacct))
   out=run/'artifacts/h9_e2e/up.txt'; self.assertEqual(out.read_text(),'alpha:one\n'); os.chmod(out,0o600)
   env['H9_TEST_OUTPUT_NAME']='down'
   with patch.dict(os.environ,env,clear=False): down=controller.submit(package,run,'selftest_downstream',['beta','two'],[f'artifacts/h9_e2e/up.txt={runtime.sha(out)}'],up['job_id'],str(sbatch),str(scontrol),str(sacct))
   self.assertEqual((run/'artifacts/h9_e2e/down.txt').read_text(),'beta:two\n'); self.assertEqual(down['dependency_afterok'],up['job_id'])

if __name__=='__main__': unittest.main()

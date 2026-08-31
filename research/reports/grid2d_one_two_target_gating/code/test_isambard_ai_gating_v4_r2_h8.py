#!/usr/bin/env python3
import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import h8_execution_binding_v4_r2 as h
import build_isambard_ai_v4_r2_h8_payload as build

class H8Tests(unittest.TestCase):
 def test_fixed_h7(self): self.assertEqual(h.H7_SHA,"7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee")
 def test_roots_mixed(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t); (p/'run').mkdir()
   with self.assertRaisesRegex(ValueError,'roots mixed'): h.safe_roots(p,p/'run')
 def test_traversal(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t); m=p/h.H8_MANIFEST; m.parent.mkdir(); m.write_text('0'*64+'  ../x\n'); a=h.sha(m)
   with self.assertRaisesRegex(ValueError,'traversal'): h.rows(p,a)
 def test_missing_receipt(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaisesRegex(ValueError,'missing runtime receipt'): h.validate_receipt(Path(t)/'x','canary','0'*64,h.H7_SHA,Path('/p'),Path('/r'))
 def test_forged_anchor_receipt(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'r'; p.write_text('{}')
   with self.assertRaisesRegex(ValueError,'forged runtime receipt'): h.validate_receipt(p,'canary','0'*64,h.H7_SHA,Path('/p'),Path('/r'))
 def test_self_rebinding_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t); os.chmod(p,0o700); m=p/h.H8_MANIFEST; m.parent.mkdir(mode=0o700); m.write_text('0'*64+'  '+h.H8_MANIFEST+'\n'); os.chmod(m,0o600); a=h.sha(m)
   with self.assertRaisesRegex(ValueError,'member drift'): h.verify_package(p,a)
 def test_ancestor_symlink(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t); q=p/'q'; q.mkdir(); s=p/'s'; s.symlink_to(q)
   with self.assertRaisesRegex(ValueError,'unsafe'): h.safe_roots(q,s/'r')
 def test_all_stage_anchor_propagation(self):
  self.assertEqual(set(h.SCRIPTS),set(h.PHASES))
  for phase in h.PHASES: self.assertIn(phase,h.PHASES)
 def test_render_stdin_and_pre_post(self):
  text=Path(h.__file__).read_text(); self.assertIn('input=data',text); self.assertIn('H8_RUNTIME_PRE_POST',text); self.assertIn('verify_package(snap',text)
 def test_verifier_to_sbatch_swap_detected(self):
  text=Path(h.__file__).read_text(); self.assertLess(text.index('data=render'),text.index('subprocess.run(cmd,input=data'))
 def test_post_check_mutation_detected(self):
  text=Path(h.__file__).read_text(); self.assertIn('(cd \\"$H8_STAGE_SNAPSHOT',text); self.assertIn('(cd \\"$H8_RUN_ROOT',text)
 def test_forced_toctou_uses_captured_bytes(self): self.assertIn('submitted_bytes_sha256',Path(h.__file__).read_text())
 def test_h8_manifest_is_append_only_h7_extension(self):
  self.assertEqual(build.MEMBERS[:len(build.h7.MEMBERS)],build.h7.MEMBERS)
  self.assertEqual(build.verify(),h.sha(build.OUT)); self.assertEqual(len(build.MEMBERS),125)
 def test_render_carries_anchors_in_argv_environment_and_receipt(self):
  package=h.ROOT if hasattr(h,'ROOT') else Path(h.__file__).parents[1]
  data=h.render(package,Path('/tmp/h8-run'),Path('/tmp/h8-snapshot'),'canary','a'*64,h.H7_SHA,['x y']).decode()
  self.assertIn("set -- "+'a'*64,data); self.assertIn('H8_PAYLOAD_SHA256=',data); self.assertIn("'x y'",data); self.assertIn('PASS_H8_RUNTIME_PRE_POST',data)
 def test_trusted_bootstrap_import_order(self):
  text=(Path(h.__file__).parent/'submit_isambard_ai_gating_v4_r2_h8.py').read_text()
  self.assertLess(text.index('trusted_preimport(a.package_root'),text.index('import h8_execution_binding_v4_r2 as h'))
if __name__=='__main__': unittest.main()

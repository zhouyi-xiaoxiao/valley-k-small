#!/usr/bin/env python3
import hashlib,json,math,tempfile,unittest
from pathlib import Path
import numpy as np
import build_gating_campaign_manifest_v4_r2 as build
import reduce_gpu_gating_v3 as v3reduce
import reduce_gpu_gating_v4_r2 as reduce

ROOT=Path(__file__).resolve().parents[1]
class Config:
 def __init__(self,i):self.cell_id=i
class Cell:
 def __init__(self,i):self.config=Config(i);self.slurm_array_job_id="8000";self.slurm_array_task_id=str(i%480);self.slurm_job_id=str(9000+i%480)
def receipt(path:Path,mutate=None):
 lines=["JobIDRaw|JobID|ArrayJobID|ArrayTaskID|State|ExitCode|ElapsedRaw|AllocTRES|ReqTRES|NNodes"]
 for t in range(480):
  row=[str(9000+t),f"8000_{t}","8000",str(t),"COMPLETED","0:0","3600","billing=1,gres/gpu=4","billing=1,gres/gpu=4","1"]
  if mutate and t==mutate[0]:row[mutate[1]]=mutate[2]
  lines.append("|".join(row))
 path.write_text("\n".join(lines)+"\n")
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((ROOT/"artifacts/data/gating_v4_r2_production_manifest.json").read_text());cls.cells=[Cell(i) for i in range(23040)]
 def test_old_payload_unchanged(self):self.assertEqual(hashlib.sha256((ROOT/"notes/isambard_ai_v4_payload.sha256").read_bytes()).hexdigest(),"3752b36338c732483b0aa739331abbff0e9999be8f4c83ad34461d65ef856485")
 def test_reflect_not_wrap(self):
  side=json.loads((ROOT/"artifacts/data/disorder_field_pack_v4_r2_reflect.manifest.json").read_text());self.assertEqual(side["definition"]["smoothing"]["mode"],"reflect");self.assertNotEqual(side["pack"]["sha256"],"b4a2a4a21621a681f73cb653d84dd9d127394732b73edb8cb7b4fce5c592d68d")
 def test_full_campaign_contract(self):
  c=v3reduce._campaign_contract(self.manifest);self.assertEqual(c["primary_target2"],(32,24));self.assertEqual(c["primary_rope"],(-.002,.002));self.assertEqual(c["tail_anchors"],((24,24),(32,24),(40,24)))
 def test_stage_a_scaled(self):
  a=[x for x in self.manifest["preregistration"]["stages"] if x["stage_id"]=="A"];self.assertEqual(len(a),1);self.assertEqual(a[0]["task_count"],1536)
 def test_cell_map(self):self.assertEqual({t+480*(g+4*k) for t in range(480) for g in range(4) for k in range(12)},set(range(23040)))
 def test_field_seeds_no_collision(self):
  with np.load(ROOT/"artifacts/data/disorder_field_pack_v4_r2_reflect.npz") as z:r=set(map(int,z["seeds"]))
  with np.load(ROOT/"artifacts/data/disorder_field_pack_v3.npz") as z:v=set(map(int,z["seeds"]))
  self.assertEqual(len(r),128);self.assertFalse(r&v)
 def test_walk_seeds_no_collision(self):self.assertFalse({build.walk_seed(i,s) for i in range(128) for s in (0,1)}&{1729+104729*i+1009*s for i in range(32) for s in (0,1)})
 def test_sacct_extended_pass(self):
  with tempfile.TemporaryDirectory() as d:p=Path(d)/"s";receipt(p);x=reduce.validate_sacct(p,self.cells);self.assertEqual(x["actual_full_node_nhr"],480.0)
 def _bad(self,column,value):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"s";receipt(p,(7,column,value))
   with self.assertRaises(Exception):reduce.validate_sacct(p,self.cells)
 def test_sacct_reject_gpu(self):self._bad(7,"gres/gpu=3")
 def test_sacct_reject_elapsed(self):self._bad(6,"0")
 def test_sacct_reject_nodes(self):self._bad(9,"2")
 def test_sacct_reject_state(self):self._bad(4,"FAILED")
 def test_wrap_marked_unpoolable(self):self.assertIn("forbidden",self.manifest["preregistration"]["initial_v4_wrap_boundary"]["classification"])
 def test_bootstrap_seeds_frozen(self):
  c=self.manifest["preregistration"]["combined_analysis"];self.assertEqual(c["v4_only"]["seed"],2026072700);self.assertEqual(c["pooled"]["seed"],2026072701)
if __name__=="__main__":unittest.main()

#!/usr/bin/env python3
"""Build append-only H10 payload over frozen H9."""
import hashlib,os,tempfile
from pathlib import Path
import build_isambard_ai_v4_r2_h9_payload as h9
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'notes/isambard_ai_v4_r2_h10_payload.sha256'
H9_SHA='a00f515ab15bd25c2c6a028420ca4339d69ce13d3abf07ce78eff688eb470bfa'
NEW=('notes/isambard_ai_v4_r2_h9_payload.sha256','notes/isambard_ai_v4_r2_h10_live_accounting_transaction_amendment.md','notes/isambard_ai_v4_r2_h10_sacct_live_array_fixture.psv','notes/isambard_ai_v4_r2_h10_sacct_live_nonarray_fixture.psv','code/h10_runtime_v4_r2.py','code/build_isambard_ai_v4_r2_h10_payload.py','code/test_isambard_ai_gating_v4_r2_h10.py')
MEMBERS=h9.MEMBERS+NEW
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def lines():
 if h9.verify()!=H9_SHA or tuple(MEMBERS[:len(h9.MEMBERS)])!=tuple(h9.MEMBERS) or len(MEMBERS)!=len(set(MEMBERS)): raise ValueError('frozen H9 append-only drift')
 return [f'{sha(ROOT/n)}  {n}' for n in MEMBERS]
def verify():
 if OUT.read_text().splitlines()!=lines(): raise ValueError('H10 payload drift')
 return sha(OUT)
def build():
 if OUT.exists() or OUT.is_symlink(): raise FileExistsError('H10 append-only')
 fd,n=tempfile.mkstemp(prefix='.h10-manifest.',dir=OUT.parent); p=Path(n)
 try:
  with os.fdopen(fd,'wb') as f: f.write(('\n'.join(lines())+'\n').encode()); f.flush(); os.fsync(f.fileno())
  os.chmod(p,0o600); os.link(p,OUT)
 finally: p.unlink(missing_ok=True)
 return verify()
if __name__=='__main__': print(verify() if OUT.exists() else build())

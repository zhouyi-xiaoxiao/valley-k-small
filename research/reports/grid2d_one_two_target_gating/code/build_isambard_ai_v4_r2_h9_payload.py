#!/usr/bin/env python3
"""Build the append-only H9 closed-world payload over immutable H8."""
import hashlib,os,tempfile
from pathlib import Path
import build_isambard_ai_v4_r2_h8_payload as h8
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'notes/isambard_ai_v4_r2_h9_payload.sha256'
H8_SHA='bb815db83632e67bf5b6c2d6f527bed2b3f9eaae4e1ac5c668a761b38065297a'
NEW=('notes/isambard_ai_v4_r2_h8_payload.sha256','notes/isambard_ai_v4_r2_h9_execution_authority_amendment.md','code/h9_runtime_v4_r2.py','code/isambard_ai_gating_v4_r2_terminal_h9.sbatch','code/isambard_ai_gating_v4_r2_selftest_h9.sbatch','code/build_isambard_ai_v4_r2_h9_payload.py','code/test_isambard_ai_gating_v4_r2_h9.py')
MEMBERS=h8.MEMBERS+NEW
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def lines():
 if h8.verify()!=H8_SHA or len(MEMBERS)!=len(set(MEMBERS)) or tuple(MEMBERS[:len(h8.MEMBERS)])!=tuple(h8.MEMBERS): raise ValueError('H8 append-only parent drift')
 return [f'{sha(ROOT/n)}  {n}' for n in MEMBERS]
def verify():
 if OUT.read_text().splitlines()!=lines(): raise ValueError('H9 payload drift')
 return sha(OUT)
def build():
 if OUT.exists() or OUT.is_symlink(): raise FileExistsError('H9 append-only')
 fd,name=tempfile.mkstemp(prefix='.h9-manifest.',dir=OUT.parent); tmp=Path(name)
 try:
  with os.fdopen(fd,'wb') as f: f.write(('\n'.join(lines())+'\n').encode()); f.flush(); os.fsync(f.fileno())
  os.chmod(tmp,0o600); os.link(tmp,OUT)
 finally: tmp.unlink(missing_ok=True)
 return verify()
if __name__=='__main__': print(verify() if OUT.exists() else build())

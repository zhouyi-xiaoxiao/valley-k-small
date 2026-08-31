#!/usr/bin/env python3
import hashlib,os,tempfile
from pathlib import Path
import build_isambard_ai_v4_r2_h7_payload as h7
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'notes/isambard_ai_v4_r2_h8_payload.sha256'
NEW=('notes/isambard_ai_v4_r2_h7_payload.sha256','notes/isambard_ai_v4_r2_h8_execution_binding_amendment.md','code/h8_execution_binding_v4_r2.py','code/submit_isambard_ai_gating_v4_r2_h8.py','code/test_isambard_ai_gating_v4_r2_h8.py','code/build_isambard_ai_v4_r2_h8_payload.py','code/isambard_ai_gating_v4_r2_terminal_h8.sbatch')
MEMBERS=h7.MEMBERS+NEW
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lines():
 assert h7.verify()=="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee" and len(MEMBERS)==len(set(MEMBERS))
 return [f'{sha(ROOT/n)}  {n}' for n in MEMBERS]
def verify():
 assert OUT.read_text().splitlines()==lines(); return sha(OUT)
def build():
 if OUT.exists(): raise FileExistsError('H8 append-only')
 fd,n=tempfile.mkstemp(dir=OUT.parent); os.write(fd,('\n'.join(lines())+'\n').encode()); os.fsync(fd); os.close(fd); os.chmod(n,0o600); os.link(n,OUT); os.unlink(n); return verify()
if __name__=='__main__': print(verify() if OUT.exists() else build())

#!/usr/bin/env python3
"""Trusted bootstrap: closed-world verify before importing any package code."""
import argparse,hashlib,json,os,re,stat,sys
from pathlib import Path

H7="7cb7c5d0d6e34e9133ce74d81da69c4814ebd9db5af30081ae1a426abefcceee"
MAN="notes/isambard_ai_v4_r2_h8_payload.sha256"
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def trusted_preimport(root,anchor,h7):
 root=root.absolute(); m=root/MAN
 if root.is_symlink() or stat.S_IMODE(root.lstat().st_mode)!=0o700: raise ValueError('trusted pre-import root mode')
 if not re.fullmatch('[0-9a-f]{64}',anchor) or digest(m)!=anchor or h7!=H7: raise ValueError('trusted pre-import anchor drift')
 rows=[]
 for line in m.read_text().splitlines():
  z=re.fullmatch(r'([0-9a-f]{64})  ([^\x00\r\n]+)',line)
  if not z or Path(z.group(2)).is_absolute() or '..' in Path(z.group(2)).parts: raise ValueError('trusted pre-import manifest syntax')
  rows.append(z.groups())
 expected={n for _,n in rows}|{MAN}; actual=set()
 for cur,ds,fs in os.walk(root,followlinks=False):
  for d in ds:
   p=Path(cur)/d
   if p.is_symlink() or stat.S_IMODE(p.lstat().st_mode)!=0o700: raise ValueError('trusted pre-import directory mode')
  for f in fs:
   p=Path(cur)/f; s=p.lstat()
   if not stat.S_ISREG(s.st_mode) or p.is_symlink() or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600: raise ValueError('trusted pre-import unsafe member')
   actual.add(p.relative_to(root).as_posix())
 if actual!=expected or any(digest(root/n)!=d for d,n in rows) or digest(root/'notes/isambard_ai_v4_r2_h7_payload.sha256')!=h7: raise ValueError('trusted pre-import closed-world drift')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--run-root',type=Path,required=True); p.add_argument('--phase',required=True); p.add_argument('--h8-payload-sha256',required=True); p.add_argument('--h7-payload-sha256',required=True); p.add_argument('--dependency'); p.add_argument('stage_args',nargs='*'); a=p.parse_args()
 trusted_preimport(a.package_root,a.h8_payload_sha256,a.h7_payload_sha256)
 sys.path.insert(0,str(a.package_root/'code')); import h8_execution_binding_v4_r2 as h
 if a.phase not in h.PHASES: raise ValueError('unknown phase')
 print(json.dumps(h.submit(package=a.package_root,run=a.run_root,phase=a.phase,h8=a.h8_payload_sha256,h7=a.h7_payload_sha256,args=a.stage_args,dependency=a.dependency),sort_keys=True)); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except (ValueError,OSError,json.JSONDecodeError) as e: print('FAIL-CLOSED:',e,file=os.sys.stderr); raise SystemExit(2)

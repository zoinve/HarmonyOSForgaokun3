"""ELF/runtime provenance gate; not a target rendering or desktop test."""
import subprocess,sys

payload=r'''
from pathlib import Path
import hashlib,json,re,subprocess,sys
r=Path('/home/zoinve/harmony-virgl-883')
if '--baseline' in sys.argv:
 p=r/'native-original-graphics-bundle-001/bundle/system/lib64/lab-freedreno003/libgallium-25.0.1.so'
else:
 work=r/'commercial-mesa-011';m=json.loads((work/'result.json').read_text());assert m['build_success']
 p=work/'stage/system/lib64/lab-commercial011/libgallium-25.0.1.so'
 needed=[]
 for row in m['artifacts']:
  f=work/'stage'/row['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
  needed+=re.findall(r'\(NEEDED\).*?\[(.*?)\]',row.get('dynamic',''))
 assert 'libc++_shared.so' not in needed
 assert m['sdk_runtime_libraries_used'] is False and m['original_commercial_runtime_linked']
dynamic=subprocess.check_output(['readelf','-d',str(p)],text=True)
needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
assert 'libc++.so' in needed and 'libc++_shared.so' not in needed,needed
undefined=subprocess.check_output(['nm','-D','--undefined-only',str(p)],text=True)
assert '_ZNSt4__n1' not in undefined,'NDK C++ ABI still required'
runtime=r/'commercial-graphics-link-009/runtime/libc++.so'
exports={line.split()[-1].split('@')[0] for line in subprocess.check_output(['nm','-D','--defined-only',str(runtime)],text=True).splitlines() if line.split()}
required={line.split()[-1].split('@')[0] for line in undefined.splitlines() if line.split() and line.split()[0]=='U' and line.split()[-1].startswith('_Z')}
assert not required-exports,sorted(required-exports)
print('PASS: actual Mesa links ISO libc++ ABI, no SDK C++ runtime dependency; target rendering untested')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-']+sys.argv[1:],input=payload,text=True,timeout=60).returncode)

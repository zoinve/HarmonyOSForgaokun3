"""Offline artifacts and runtime provenance, not target display acceptance."""
from pathlib import Path
import subprocess
assert Path(__file__).with_name('build-commercial-graphics-014.py').is_file(), 'missing commercial graphics bridge build'
payload=r'''
from pathlib import Path
import json,hashlib,subprocess,re
r=Path('/home/zoinve/harmony-virgl-883');w=r/'commercial-graphics-014'
m=json.loads((w/'result.json').read_text())
for name,digest in m['graphics_sha256'].items():
 p=w/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
 assert 'libc++_shared.so' not in dynamic
 assert b'/system/lib64/lab-commercial013/' in p.read_bytes()
 trace=(w/m['graphics_link_traces'][name]).read_text()
 assert str(w/'runtime/libc++.so') in trace and str(w/'runtime/libc.so') in trace
 assert '/platform-root/' not in trace
 assert not any('/sdk/' in l and l.strip().endswith('.so') for l in trace.splitlines())
assert not m['deployed'] and not m['sdk_system_libraries_used']
print('PASS: own EGL/composer artifacts, commercial runtime link traces, new Mesa path; target runtime unverified')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

"""Link provenance is not commercial graphics runtime acceptance."""
from pathlib import Path
import json, subprocess
base=Path(__file__).resolve().parent
assert (base/'build-commercial-graphics-link-009.py').is_file(), 'missing commercial-runtime hardware build'
payload=r'''
from pathlib import Path
import json,hashlib
r=Path('/home/zoinve/harmony-virgl-883/commercial-graphics-link-009')
m=json.loads((r/'result.json').read_text())
assert m['sdk_system_libraries_used'] is False
assert m['original_commercial_libc_and_libcxx'] is True
assert m['original_services_replaced'] is False
assert hashlib.sha256((r/'libdisplay_composer_vdi_impl.z.so').read_bytes()).hexdigest()==m['sha256']
trace=(r/m['link_trace_file']).read_text()
assert str(r/'runtime/libc.so') in trace and str(r/'runtime/libc++.so') in trace
assert '/platform-root/' not in trace
assert not any('/sdk/' in l and l.strip().endswith('.so') for l in trace.splitlines())
print('PASS: own hardware source links original commercial libc/libc++; target ABI and display unverified')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

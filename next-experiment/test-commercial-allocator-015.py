"""Offline real ELF/link gate, not a claim of commercial HDI compatibility."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'build-commercial-allocator-015.py').is_file(),'missing commercial-runtime allocator build'
payload=r'''
from pathlib import Path
import hashlib,json,subprocess,re
w=Path('/home/zoinve/harmony-virgl-883/commercial-allocator-015')
m=json.loads((w/'result.json').read_text());p=w/'libdisplay_buffer_vdi_impl.z.so'
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
assert not m['sdk_system_libraries_used'] and m['original_commercial_libc_and_libcxx']
t=(w/m['link_trace_file']).read_text()
assert str(w/'runtime/libc.so') in t and str(w/'runtime/libc++.so') in t
assert '/platform-root/' not in t and not any('/sdk/' in l and l.strip().endswith('.so') for l in t.splitlines())
d=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
assert 'libc++_shared.so' not in d
n=subprocess.check_output(['aarch64-linux-gnu-nm','-D',str(p)],text=True)
assert ' T CreateDisplayBufferVdi' in n and ' T DestroyDisplayBufferVdi' in n
exports=subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(w/'runtime/libc++.so')],text=True)
exported={l.split()[-1].split('@')[0] for l in exports.splitlines() if l.split()}
needed={l.split()[-1].split('@')[0] for l in n.splitlines() if ' U _Z' in l}
assert not needed-exported,sorted(needed-exported)
print('PASS: own allocator, original commercial libc/libc++, real exports; target ABI and display NOT verified')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

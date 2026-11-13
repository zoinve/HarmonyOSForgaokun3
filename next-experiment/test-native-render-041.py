"""Native build contract, distinct from real service/runtime acceptance."""
from pathlib import Path
import subprocess
assert Path(__file__).with_name('build-native-render-041.py').is_file(),'missing native GPU composer integration'
payload=r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'native-render-041'
r=json.loads((work/'result.json').read_text())
for name,digest in r['sha256'].items():assert hashlib.sha256((work/name).read_bytes()).hexdigest()==digest
s=(work/'composer-trace.cpp').read_text()
assert 'NativeGpu041::frame(' in s and 'DRM_IOCTL_GEM_CLOSE' in s
assert 'NativeGpu041::shutdown();' in s and 'cached_landscape_copy_034(' in s
assert 'composer_gpu_two_pass041' in s
assert r['old034_unchanged'] and not r['input_injection']
print('PASS: AArch64 GPU composer artifacts, original hashes and CPU fallback contract; runtime not verified')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

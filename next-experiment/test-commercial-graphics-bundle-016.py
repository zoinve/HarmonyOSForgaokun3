"""Offline payload/provenance gate, not commercial graphics runtime acceptance."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-commercial-graphics-bundle-016.py').is_file(), 'missing commercial board graphics bundle'
p=runpy.run_path(str(base/'build-commercial-graphics-bundle-016.py'))
assert 'setuid' not in p['render_launcher'] and 'LD_PRELOAD=' not in p['render_launcher']
assert 'exec /system/bin/render_service' in p['render_launcher']
assert 'exec /vendor/bin/hdf_devhost' in p['host_launcher']
assert 'l410_mali_r18_gpu_helper' not in p['host_launcher']
payload=r'''
from pathlib import Path
import json,hashlib,subprocess
r=Path('/home/zoinve/harmony-virgl-883/commercial-graphics-bundle-016')
m=json.loads((r/'result.json').read_text())
assert not m['sdk_system_libraries_used'] and not m['original_service_definitions_changed']
assert m['gpu_api_parameter_changes']=={'persist.sys.graphic.GpuApitype':['1','0']}
for item in m['files']:
 p=r/'tree'/item['target'].lstrip('/')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
 assert p.name not in ['libc.so','libc++.so','libc++_shared.so']
 if p.read_bytes()[:4]==b'\x7fELF':
  needed=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
  assert 'libc++_shared.so' not in needed
assert m['original_parameter_other_lines_unchanged']
print('PASS: commercial-runtime board libraries, original services retained, graphics parameter only; runtime unverified')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

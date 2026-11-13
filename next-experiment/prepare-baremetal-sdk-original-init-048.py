"""Import original vendor HDF services, preserving all original service identities."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess


def patch_config(raw):
    config = json.loads(raw)
    target = '/vendor/etc/init/hdf_devhost.cfg'
    assert isinstance(config['import'], list) and target not in config['import']
    config['import'] = config['import'] + [target]
    return (json.dumps(config, indent=2) + '\n').encode()


parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-047.py')))
source = parent['source'].replace('ORIGINAL_INIT047_', 'ORIGINAL_INIT048_').replace('GRAPHICS047_', 'GRAPHICS048_')
source = source.replace('sample < 12', 'sample < 24').replace('sample == 9', 'sample == 9 || sample == 21')
anchor = '    guest_permissive_config_047();'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
    if (mount("/graphics-init.cfg", "/system/etc/init.cfg", NULL, MS_BIND, NULL) ||
        mount(NULL, "/system/etc/init.cfg", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL))
        fail("guest-only original HDF service import bind");
    dprintf(1, "GRAPHICS048_VENDOR_IMPORT original_service_config=1 service_credentials_unmodified=1\\n");''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-047', 'baremetal-sdk-original-init-048')
anchor = "policy=dump('vendor.img'"
assert payload.count(anchor) == 1
addition = inspect.getsource(patch_config) + '''
original_init=dump('system.img','/system/etc/init.cfg','original-init.cfg')
original_hdf=dump('vendor.img','/etc/init/hdf_devhost.cfg','original-hdf-devhost.cfg')
original=json.loads(original_init.read_bytes())
patched=patch_config(original_init.read_bytes())
checked=json.loads(patched)
assert checked['import']==original['import']+['/vendor/etc/init/hdf_devhost.cfg']
assert {k:v for k,v in checked.items() if k!='import'}=={k:v for k,v in original.items() if k!='import'}
services=json.loads(original_hdf.read_bytes())['services']
for name in ['composer_host','allocator_host']:
 row=next(s for s in services if s['name']==name)
 assert row['uid']==name and row['secon']=='u:r:'+name+':s0'
with (work/'graphics-init.cfg').open('xb') as f:f.write(patched)
(local/'graphics-init.cfg').write_bytes(patched)
'''
payload = payload.replace(anchor, addition + anchor)
anchor = "for p in [work/'init',policy]"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "for p in [work/'init',policy,work/'graphics-init.cfg']")
compile(payload, 'original-graphics-048-build', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=180)
    raise SystemExit(result.returncode)

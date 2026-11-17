"""Stage the public diagnostic executable outside ESP; no keys or host configuration."""
from pathlib import Path
import base64
import json
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/live-debug-helper-161'
REMOTE = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-helper-161'

PREPARE = r'''
from pathlib import Path
import base64,hashlib,json,os
root=Path(REMOTE_ROOT)
assert os.geteuid()==0 and not root.exists()
data=base64.b64decode(BINARY_BASE64,validate=True)
assert hashlib.sha256(data).hexdigest()==BINARY_SHA256
assert data[:4]==b'\x7fELF' and int.from_bytes(data[18:20],'little')==183
root.mkdir(mode=0o700)
binary=root/'live-debug161'
binary.open('xb').write(data);binary.chmod(0o500)
assert hashlib.sha256(binary.read_bytes()).hexdigest()==BINARY_SHA256
result=dict(path=str(binary),sha256=BINARY_SHA256,bytes=len(data),mode='0500',uid=binary.stat().st_uid,
 boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),executed=False,private_keys_read=False,
 esp_changed=False,original_images_or_host_configuration_changed=False)
(root/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
'''


if __name__ == '__main__':
    assert not REPORT.exists()
    metadata = json.loads((ROOT / 'reports/commercial61-native-161/result.json').read_text())
    assert all(json.loads((ROOT / 'reports/commercial61-native-161/admission-test.json').read_text()).values())
    data = Path('/home/zoinve/harmony-virgl-883/commercial61-native-161/live-debug161').read_bytes()
    source = PREPARE.replace('BINARY_BASE64',repr(base64.b64encode(data).decode())).replace('BINARY_SHA256',repr(metadata['live161']['helper_sha256']))
    transport = runpy.run_path(str(BASE / 'prepare-live-debug-156.py'))
    remote = transport['remote']
    remote.__globals__['REMOTE_ROOT'] = REMOTE
    result = remote(source)
    REPORT.mkdir()
    (REPORT / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

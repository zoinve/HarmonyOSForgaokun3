"""Fresh numbered guest after preserved build084 failure; no provider changes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-084.py')))['payload']
for old, new in [('original-init-qemu-084','original-init-qemu-085'),
                 ('harmony-sdk-qemu084-','harmony-sdk-qemu085-'),
                 ('original-init-084/result.json','original-init-085/result.json'),
                 ('GRAPHICS084_','GRAPHICS085_'), ('ORIGINAL_INIT084_','ORIGINAL_INIT085_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-profile-events-085-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'], input=payload,
                                   text=True, timeout=660).returncode)

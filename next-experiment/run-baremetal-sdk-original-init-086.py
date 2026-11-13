"""Fresh VM only: enable audit logging without changing guest access controls."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-085.py')))['payload']
for old, new in [('original-init-qemu-085', 'original-init-qemu-086'),
                 ('harmony-sdk-qemu085-', 'harmony-sdk-qemu086-'),
                 ('original-init-085/result.json', 'original-init-086/result.json'),
                 ('GRAPHICS085_', 'GRAPHICS086_'), ('ORIGINAL_INIT085_', 'ORIGINAL_INIT086_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
assert payload.count('loglevel=8 enforcing=0') == 1
payload = payload.replace('loglevel=8 enforcing=0', 'loglevel=8 audit=1 enforcing=0')
compile(payload, 'original-samgr-syscalls-086-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

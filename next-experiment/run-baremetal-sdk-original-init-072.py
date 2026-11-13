"""Same isolated graph and providers; extend passive sampling to each real PID."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-071.py')))['payload']
for old, new in [('original-init-qemu-071', 'original-init-qemu-072'),
                 ('harmony-sdk-qemu071-', 'harmony-sdk-qemu072-'),
                 ('original-init-071/result.json', 'original-init-072/result.json'),
                 ('GRAPHICS071_', 'GRAPHICS072_'), ('ORIGINAL_INIT071_', 'ORIGINAL_INIT072_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-roles-072-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

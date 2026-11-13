"""Fresh unchanged graphical guest with read-only original power-service queries."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-097.py')))['payload']
for old, new in [('original-init-qemu-097', 'original-init-qemu-098'),
                 ('original-init-097/result.json', 'original-init-098/result.json'),
                 ('harmony-sdk-qemu097-', 'harmony-sdk-qemu098-'),
                 ('GRAPHICS097_', 'GRAPHICS098_'), ('ORIGINAL_INIT097_', 'ORIGINAL_INIT098_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-power-service-098-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

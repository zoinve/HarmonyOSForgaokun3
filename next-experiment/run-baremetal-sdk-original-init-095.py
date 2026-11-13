"""Fresh unchanged graphical guest with original SceneBoard log queries."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-094.py')))['payload']
for old, new in [('original-init-qemu-094', 'original-init-qemu-095'),
                 ('original-init-094/result.json', 'original-init-095/result.json'),
                 ('harmony-sdk-qemu094-', 'harmony-sdk-qemu095-'),
                 ('GRAPHICS094_', 'GRAPHICS095_'), ('ORIGINAL_INIT094_', 'ORIGINAL_INIT095_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-sceneboard-logs-095-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

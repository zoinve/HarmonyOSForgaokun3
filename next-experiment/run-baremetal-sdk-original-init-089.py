"""Fresh isolated layout test; preserve readonly/nodev and all real services."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-088.py')))['payload']
for old, new in [('original-init-qemu-088', 'original-init-qemu-089'),
                 ('harmony-sdk-qemu088-', 'harmony-sdk-qemu089-'),
                 ('original-init-088/result.json', 'original-init-089/result.json'),
                 ('GRAPHICS088_', 'GRAPHICS089_'), ('ORIGINAL_INIT088_', 'ORIGINAL_INIT089_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-system-bind-089-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

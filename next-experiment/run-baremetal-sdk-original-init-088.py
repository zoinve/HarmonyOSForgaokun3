"""Fresh isolated guest; only the system mount layout changes from 087."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-087.py')))['payload']
for old, new in [('original-init-qemu-087', 'original-init-qemu-088'),
                 ('harmony-sdk-qemu087-', 'harmony-sdk-qemu088-'),
                 ('original-init-087/result.json', 'original-init-088/result.json'),
                 ('GRAPHICS087_', 'GRAPHICS088_'), ('ORIGINAL_INIT087_', 'ORIGINAL_INIT088_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-system-bind-088-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

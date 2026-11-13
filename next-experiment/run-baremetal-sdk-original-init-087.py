"""Fresh isolated guest; preserve graph, audit rule and original disk images."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-086.py')))['payload']
for old, new in [('original-init-qemu-086', 'original-init-qemu-087'),
                 ('harmony-sdk-qemu086-', 'harmony-sdk-qemu087-'),
                 ('original-init-086/result.json', 'original-init-087/result.json'),
                 ('GRAPHICS086_', 'GRAPHICS087_'), ('ORIGINAL_INIT086_', 'ORIGINAL_INIT087_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-audit-copy-087-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

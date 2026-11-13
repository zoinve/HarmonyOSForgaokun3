"""Unchanged full original graph, adding only bounded authentic HDF log queries."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-067.py')))['payload']
for old, new in [('original-init-qemu-067', 'original-init-qemu-068'),
                 ('harmony-sdk-qemu067-', 'harmony-sdk-qemu068-'),
                 ('original-init-067/result.json', 'original-init-068/result.json'),
                 ('GRAPHICS067_', 'GRAPHICS068_'), ('ORIGINAL_INIT067_', 'ORIGINAL_INIT068_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-068-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

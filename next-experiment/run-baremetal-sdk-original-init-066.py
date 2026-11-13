"""Bounded original service observations; same known software-Mesa bundle."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-064.py')))['payload']
for old, new in [('original-init-qemu-064', 'original-init-qemu-066'),
                 ('harmony-sdk-qemu064-', 'harmony-sdk-qemu066-'),
                 ('original-init-064/result.json', 'original-init-066/result.json'),
                 ('GRAPHICS064_', 'GRAPHICS066_'), ('ORIGINAL_INIT064_', 'ORIGINAL_INIT066_')]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-066-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

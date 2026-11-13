"""Identical original graph; only bounded read-only parameter observation differs."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-081.py')))['payload']
for old, new in [('original-init-qemu-081', 'original-init-qemu-082'),
                 ('harmony-sdk-qemu081-', 'harmony-sdk-qemu082-'),
                 ('original-init-081/result.json', 'original-init-082/result.json'),
                 ('GRAPHICS081_', 'GRAPHICS082_'), ('ORIGINAL_INIT081_', 'ORIGINAL_INIT082_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-config-policy-082-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

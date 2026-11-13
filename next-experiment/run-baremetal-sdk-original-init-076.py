"""Capture actual scanout with real Commit results and passive process snapshots."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-075.py')))['payload']
for old, new in [('original-init-qemu-075', 'original-init-qemu-076'),
                 ('harmony-sdk-qemu075-', 'harmony-sdk-qemu076-'),
                 ('original-init-074/result.json', 'original-init-076/result.json'),
                 ('GRAPHICS074_', 'GRAPHICS076_'), ('ORIGINAL_INIT074_', 'ORIGINAL_INIT076_'),
                 ('original-graphics-provider-004', 'original-graphics-provider-005')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-content-076-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

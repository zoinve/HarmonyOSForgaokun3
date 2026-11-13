"""Bounded original-service observation with trace load/path witnesses."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-055.py')))['payload']
for old, new in [('original-init-qemu-055', 'original-init-qemu-056'),
                 ('harmony-sdk-qemu055-', 'harmony-sdk-qemu056-'),
                 ('original-init-055', 'original-init-056'),
                 ('ORIGINAL_INIT055_', 'ORIGINAL_INIT056_'),
                 ('GRAPHICS055_', 'GRAPHICS056_'),
                 ('original-graphics-egl-003/result.json', 'original-graphics-egl-004/result.json')]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-056-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

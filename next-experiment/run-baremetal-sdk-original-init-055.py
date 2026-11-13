"""One bounded full original-service boot with reversible bridge diagnostics."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-054.py')))['payload']
for old, new in [('original-init-qemu-054', 'original-init-qemu-055'),
                 ('harmony-sdk-qemu054-', 'harmony-sdk-qemu055-'),
                 ('original-init-054', 'original-init-055'),
                 ('ORIGINAL_INIT054_', 'ORIGINAL_INIT055_'),
                 ('GRAPHICS054_', 'GRAPHICS055_'),
                 ('original-graphics-egl-002/result.json', 'original-graphics-egl-003/result.json')]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-055-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

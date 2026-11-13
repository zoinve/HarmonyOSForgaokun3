"""Change only the RAM alias for the actual GBM backend search path."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-058.py')))['payload']
for old, new in [('original-init-qemu-058', 'original-init-qemu-059'),
                 ('harmony-sdk-qemu058-', 'harmony-sdk-qemu059-'),
                 ('original-init-056', 'original-init-059'),
                 ('ORIGINAL_INIT056_', 'ORIGINAL_INIT059_'),
                 ('GRAPHICS056_', 'GRAPHICS059_')]:
    assert old in payload
    payload = payload.replace(old, new)
assert 'original-graphics-egl-006/result.json' in payload
compile(payload, 'original-graphics-059-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

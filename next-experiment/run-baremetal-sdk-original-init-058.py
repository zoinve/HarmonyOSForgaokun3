"""Observe real display-creation stages in the original service graph."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-057.py')))['payload']
for old, new in [('original-init-qemu-057', 'original-init-qemu-058'),
                 ('harmony-sdk-qemu057-', 'harmony-sdk-qemu058-'),
                 ('original-graphics-egl-005/result.json', 'original-graphics-egl-006/result.json')]:
    assert old in payload
    payload = payload.replace(old, new)
assert 'baremetal-sdk-original-init-056/result.json' in payload
compile(payload, 'original-graphics-058-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

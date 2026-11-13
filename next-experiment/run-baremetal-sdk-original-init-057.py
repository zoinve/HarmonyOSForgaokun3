"""Reuse verified 056 bootstrap; change only the trace budget in the bridge."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-056.py')))['payload']
for old, new in [('original-init-qemu-056', 'original-init-qemu-057'),
                 ('harmony-sdk-qemu056-', 'harmony-sdk-qemu057-'),
                 ('original-graphics-egl-004/result.json', 'original-graphics-egl-005/result.json')]:
    assert old in payload
    payload = payload.replace(old, new)
assert 'baremetal-sdk-original-init-056/result.json' in payload
compile(payload, 'original-graphics-057-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

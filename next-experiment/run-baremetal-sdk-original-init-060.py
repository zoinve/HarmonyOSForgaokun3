"""Same original-service fixture, with failure-only loader diagnostics."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-059.py')))['payload']
for old, new in [('original-init-qemu-059', 'original-init-qemu-060'),
                 ('harmony-sdk-qemu059-', 'harmony-sdk-qemu060-'),
                 ('original-graphics-egl-006/result.json', 'original-graphics-egl-007/result.json')]:
    assert old in payload
    payload = payload.replace(old, new)
assert 'original-init-059/result.json' in payload
compile(payload, 'original-graphics-060-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

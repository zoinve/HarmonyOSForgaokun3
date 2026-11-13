"""Use the actual published bundle manifest; preserve failed trial061."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-061.py')))['payload']
for old, new in [('original-init-qemu-061', 'original-init-qemu-062'),
                 ('harmony-sdk-qemu061-', 'harmony-sdk-qemu062-'),
                 ("root/'original-graphics-egl-008/result.json'", "local.parent/'original-graphics-egl-008/result.json'")]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-062-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

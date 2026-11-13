"""Same real software graphics stack, with targeted original-service logs."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-062.py')))['payload']
for old, new in [('original-init-qemu-062', 'original-init-qemu-063'),
                 ('harmony-sdk-qemu062-', 'harmony-sdk-qemu063-'),
                 ('original-init-059/result.json', 'original-init-063/result.json'),
                 ('GRAPHICS059_', 'GRAPHICS063_'),
                 ('ORIGINAL_INIT059_', 'ORIGINAL_INIT063_')]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-063-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

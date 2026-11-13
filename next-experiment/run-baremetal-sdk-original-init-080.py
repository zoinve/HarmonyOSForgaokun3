"""Keep the original graph/desktop requests and change only passive log selection."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-079.py')))['payload']
for old, new in [('original-init-qemu-079', 'original-init-qemu-080'),
                 ('harmony-sdk-qemu079-', 'harmony-sdk-qemu080-'),
                 ('original-init-079/result.json', 'original-init-080/result.json'),
                 ('GRAPHICS079_', 'GRAPHICS080_'), ('ORIGINAL_INIT079_', 'ORIGINAL_INIT080_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-bms-head-080-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

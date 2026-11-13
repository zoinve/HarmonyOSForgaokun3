"""Same isolated service graph with wider passive task sampling only."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-072.py')))['payload']
for old, new in [('original-init-qemu-072', 'original-init-qemu-073'),
                 ('harmony-sdk-qemu072-', 'harmony-sdk-qemu073-'),
                 ('original-init-072/result.json', 'original-init-073/result.json'),
                 ('GRAPHICS072_', 'GRAPHICS073_'), ('ORIGINAL_INIT072_', 'ORIGINAL_INIT073_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-workers-073-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

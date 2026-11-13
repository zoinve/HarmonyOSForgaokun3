"""Same full original graph and desktop requests; correct only the log query."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-078.py')))['payload']
for old, new in [('original-init-qemu-078', 'original-init-qemu-079'),
                 ('harmony-sdk-qemu078-', 'harmony-sdk-qemu079-'),
                 ('original-init-078/result.json', 'original-init-079/result.json'),
                 ('GRAPHICS078_', 'GRAPHICS079_'), ('ORIGINAL_INIT078_', 'ORIGINAL_INIT079_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-foundation-tail-079-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

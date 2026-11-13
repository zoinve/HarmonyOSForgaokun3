"""Fresh original graphical guest, restoring only original /mnt early mount."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-093.py')))['payload']
for old, new in [('original-init-qemu-093', 'original-init-qemu-094'),
                 ('original-init-093/result.json', 'original-init-094/result.json'),
                 ('harmony-sdk-qemu093-', 'harmony-sdk-qemu094-'),
                 ('GRAPHICS093_', 'GRAPHICS094_'), ('ORIGINAL_INIT093_', 'ORIGINAL_INIT094_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-runtime-mnt-094-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

"""Fresh unchanged graphical guest with bounded original AppSpawn log queries."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-092.py')))['payload']
for old, new in [('original-init-qemu-092', 'original-init-qemu-093'),
                 ('original-init-092/result.json', 'original-init-093/result.json'),
                 ('harmony-sdk-qemu092-', 'harmony-sdk-qemu093-'),
                 ('GRAPHICS092_', 'GRAPHICS093_'), ('ORIGINAL_INIT092_', 'ORIGINAL_INIT093_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-appspawn-observation-093-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

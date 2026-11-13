"""Fresh unchanged graphical guest with cheaper passive application observation."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-095.py')))['payload']
for old, new in [('original-init-qemu-095', 'original-init-qemu-096'),
                 ('original-init-095/result.json', 'original-init-096/result.json'),
                 ('harmony-sdk-qemu095-', 'harmony-sdk-qemu096-'),
                 ('GRAPHICS095_', 'GRAPHICS096_'), ('ORIGINAL_INIT095_', 'ORIGINAL_INIT096_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-sceneboard-late-096-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

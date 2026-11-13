"""Same isolated graph, tools and providers; add passive original Foundation logs."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-077.py')))['payload']
for old, new in [('original-init-qemu-077', 'original-init-qemu-078'),
                 ('harmony-sdk-qemu077-', 'harmony-sdk-qemu078-'),
                 ('original-init-077/result.json', 'original-init-078/result.json'),
                 ('GRAPHICS077_', 'GRAPHICS078_'), ('ORIGINAL_INIT077_', 'ORIGINAL_INIT078_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-desktop-errors-078-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

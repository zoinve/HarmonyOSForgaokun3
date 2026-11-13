"""Fresh later-start observation, with bounded QMP captures and isolated sparse data."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-091.py')))['payload']
for old, new in [('original-init-qemu-091', 'original-init-qemu-092'),
                 ('original-init-091/result.json', 'original-init-092/result.json'),
                 ('harmony-sdk-qemu091-', 'harmony-sdk-qemu092-'),
                 ('GRAPHICS091_', 'GRAPHICS092_'), ('ORIGINAL_INIT091_', 'ORIGINAL_INIT092_'),
                 ('timeout_seconds=480', 'timeout_seconds=660'),
                 ('for target in (120,240,360,450,480)', 'for target in (120,360,480,600,650,660)'),
                 ('if target==480:', 'if target==660:')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-desktop-late-092-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

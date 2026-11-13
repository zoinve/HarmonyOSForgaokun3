"""Same original graph, normal desktop requests and bounded virtual captures."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-076.py')))['payload']
for old, new in [('original-init-qemu-076', 'original-init-qemu-077'),
                 ('harmony-sdk-qemu076-', 'harmony-sdk-qemu077-'),
                 ('original-init-076/result.json', 'original-init-077/result.json'),
                 ('GRAPHICS076_', 'GRAPHICS077_'), ('ORIGINAL_INIT076_', 'ORIGINAL_INIT077_'),
                 ('timeout_seconds=360', 'timeout_seconds=480'),
                 ('for target in (120,240,330,360):', 'for target in (120,240,360,450,480):'),
                 ('if target==360:', 'if target==480:')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-desktop-077-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

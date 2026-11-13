"""Compare fewer virtual display pixels, reusing the exact guarded guest 098."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-098.py')))['payload']
for old, new in [('original-init-qemu-098', 'original-init-qemu-099'),
                 ('harmony-sdk-qemu098-', 'harmony-sdk-qemu099-')]:
    assert old in payload, old
    payload = payload.replace(old, new)
anchor = "command+=['-device','virtio-gpu-device']"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "command+=['-device','virtio-gpu-device,xres=800,yres=600']")
assert 'baremetal-sdk-original-init-098/result.json' in payload
compile(payload, 'original-display-load-099-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

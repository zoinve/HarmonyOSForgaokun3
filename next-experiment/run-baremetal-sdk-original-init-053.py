"""Modern virtio-mmio: GPU requires VERSION_1, legacy block disks did not."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-052.py')))['payload']
for old, new in [('original-init-qemu-052', 'original-init-qemu-053'),
                 ('harmony-sdk-qemu052-', 'harmony-sdk-qemu053-')]:
    assert old in payload
    payload = payload.replace(old, new)
anchor = "command+=['-device','virtio-gpu-device']"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "command+=['-global','virtio-mmio.force-legacy=false']\n" + anchor)
compile(payload, 'original-graphics-053-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

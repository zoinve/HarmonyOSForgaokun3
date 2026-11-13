"""Original service graph with a virtual display; no physical GPU or host changes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-048.py')))['payload']
for old, new in [('original-init-qemu-048', 'original-init-qemu-049'),
                 ('harmony-sdk-qemu048-', 'harmony-sdk-qemu049-')]:
    assert old in payload
    payload = payload.replace(old, new)
anchor = "kernel=Path(storage['test_kernel']['path']);config=root/'baremetal-sdk-storage-test-004/out/.config'"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """storage=json.loads((root/'original-graphics-kernel-002/result.json').read_text())
kernel=Path(storage['test_kernel']['path']);config=root/'original-graphics-kernel-002/out/.config'""")
old = '5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d'
assert payload.count(old) == 1
payload = payload.replace(old, 'a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136')
anchor = "report=dict(bounded_observation_complete=False"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "command+=['-device','virtio-gpu-device']\n" + anchor)
payload = payload.replace('gpu_attached=False', 'gpu_attached=True')
compile(payload, 'original-graphics-049-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

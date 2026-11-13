"""Trace virtual GPU initialization after050 safely refused an unbound GPU."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-050.py')))['payload']
for old, new in [('original-init-qemu-050', 'original-init-qemu-051'),
                 ('harmony-sdk-qemu050-', 'harmony-sdk-qemu051-')]:
    assert old in payload
    payload = payload.replace(old, new)
anchor = 'console=ttyAMA0 rdinit=/init harmony.original_init_test=1'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, anchor + ' initcall_debug')
compile(payload, 'original-graphics-051-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

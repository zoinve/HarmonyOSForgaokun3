"""Expose debug-level initcall results hidden by the default console loglevel."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-051.py')))['payload']
for old, new in [('original-init-qemu-051', 'original-init-qemu-052'),
                 ('harmony-sdk-qemu051-', 'harmony-sdk-qemu052-'),
                 (' initcall_debug enforcing=0', ' initcall_debug loglevel=8 enforcing=0')]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-052-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

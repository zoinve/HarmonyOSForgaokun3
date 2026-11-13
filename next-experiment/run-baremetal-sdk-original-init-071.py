"""Unchanged original graph; bounded read-only state observations in the guest."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-070.py')))['payload']
for old, new in [('original-init-qemu-070', 'original-init-qemu-071'),
                 ('harmony-sdk-qemu070-', 'harmony-sdk-qemu071-'),
                 ('original-init-070/result.json', 'original-init-071/result.json'),
                 ('GRAPHICS070_', 'GRAPHICS071_'), ('ORIGINAL_INIT070_', 'ORIGINAL_INIT071_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-state-071-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

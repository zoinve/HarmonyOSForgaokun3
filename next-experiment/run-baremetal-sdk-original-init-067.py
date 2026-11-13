"""360-second isolated observation; unchanged kernel, providers and service identities."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-066.py')))['payload']
for old, new in [('original-init-qemu-066', 'original-init-qemu-067'),
                 ('harmony-sdk-qemu066-', 'harmony-sdk-qemu067-'),
                 ('original-init-066/result.json', 'original-init-067/result.json'),
                 ('GRAPHICS066_', 'GRAPHICS067_'), ('ORIGINAL_INIT066_', 'ORIGINAL_INIT067_'),
                 ('timeout_seconds=160', 'timeout_seconds=360'),
                 ('stdout=f,stderr=subprocess.STDOUT,timeout=160',
                  'stdout=f,stderr=subprocess.STDOUT,timeout=360')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-067-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

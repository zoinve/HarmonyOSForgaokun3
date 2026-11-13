"""Original full graph with trace-only composer VDI; physical display untouched."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-068.py')))['payload']
for old, new in [('original-init-qemu-068', 'original-init-qemu-069'),
                 ('harmony-sdk-qemu068-', 'harmony-sdk-qemu069-'),
                 ('original-init-068/result.json', 'original-init-069/result.json'),
                 ('GRAPHICS068_', 'GRAPHICS069_'), ('ORIGINAL_INIT068_', 'ORIGINAL_INIT069_'),
                 ('original-graphics-provider-002/result.json', 'original-graphics-provider-004/result.json')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-069-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

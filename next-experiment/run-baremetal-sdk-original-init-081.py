"""Same original graph, bounded passive SAMGR log/profile observation only."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-080.py')))['payload']
for old, new in [('original-init-qemu-080', 'original-init-qemu-081'),
                 ('harmony-sdk-qemu080-', 'harmony-sdk-qemu081-'),
                 ('original-init-080/result.json', 'original-init-081/result.json'),
                 ('GRAPHICS080_', 'GRAPHICS081_'), ('ORIGINAL_INIT080_', 'ORIGINAL_INIT081_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-samgr-profile-081-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

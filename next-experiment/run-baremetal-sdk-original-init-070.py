"""Same original graph and providers; passively observe guest Binder state."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-069.py')))['payload']
for old, new in [('original-init-qemu-069', 'original-init-qemu-070'),
                 ('harmony-sdk-qemu069-', 'harmony-sdk-qemu070-'),
                 ('original-init-069/result.json', 'original-init-070/result.json'),
                 ('GRAPHICS069_', 'GRAPHICS070_'), ('ORIGINAL_INIT069_', 'ORIGINAL_INIT070_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-070-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

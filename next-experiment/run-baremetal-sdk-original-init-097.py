"""Keep the original graphical guest and deadline; sample actual scanout more often."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-096.py')))['payload']
for old, new in [('original-init-qemu-096', 'original-init-qemu-097'),
                 ('original-init-096/result.json', 'original-init-097/result.json'),
                 ('harmony-sdk-qemu096-', 'harmony-sdk-qemu097-'),
                 ('GRAPHICS096_', 'GRAPHICS097_'), ('ORIGINAL_INIT096_', 'ORIGINAL_INIT097_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
old = '(120,360,480,600,650,660)'
assert payload.count(old) == 1
payload = payload.replace(old, '(120,360,480,540,570,600,620,640,650,660)')
compile(payload, 'original-rs-diagnostics-097-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)

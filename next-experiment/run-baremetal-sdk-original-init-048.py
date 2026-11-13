"""New vendor-service import regression, not a rerun of completed047."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-047.py')))['payload']
for old, new in [('original-init-qemu-047', 'original-init-qemu-048'),
                 ('original-init-047', 'original-init-048'),
                 ('harmony-sdk-qemu047-', 'harmony-sdk-qemu048-'),
                 ('ORIGINAL_INIT047_', 'ORIGINAL_INIT048_'),
                 ('GRAPHICS047_', 'GRAPHICS048_'),
                 ('timeout=90)', 'timeout=160)'),
                 ('timeout_seconds=90', 'timeout_seconds=160')]:
    assert old in payload, old
    payload = payload.replace(old, new)
anchor = "add('TRAILER!!!',0)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "add('graphics-init.cfg',stat.S_IFREG|0o444,Path(prep['files']['graphics-init.cfg']['path']).read_bytes())\n" + anchor)
compile(payload, 'original-graphics-048-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

"""Original init/HDF services plus reference VDIs on virtual display only."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-049.py')))['payload']
for old, new in [('original-init-qemu-049', 'original-init-qemu-050'),
                 ('original-init-048', 'original-init-050'),
                 ('harmony-sdk-qemu049-', 'harmony-sdk-qemu050-'),
                 ('ORIGINAL_INIT048_', 'ORIGINAL_INIT050_'),
                 ('GRAPHICS048_', 'GRAPHICS050_')]:
    assert old in payload
    payload = payload.replace(old, new)
anchor = "add('TRAILER!!!',0)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """provider=json.loads((root/'original-graphics-provider-002/result.json').read_text())
assert provider['platform_abi']=='std::__h' and len(provider['files'])==3
add('graphics-provider',stat.S_IFDIR|0o755)
for row in provider['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 add('graphics-provider/'+row['name'],stat.S_IFREG|0o444,p.read_bytes())
""" + anchor)
compile(payload, 'original-graphics-050-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=480)
    raise SystemExit(result.returncode)

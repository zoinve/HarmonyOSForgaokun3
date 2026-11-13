"""Same original graph; supply exactly the matching real ashmem kernel module."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-073.py')))['payload']
for old, new in [('original-init-qemu-073', 'original-init-qemu-074'),
                 ('harmony-sdk-qemu073-', 'harmony-sdk-qemu074-'),
                 ('original-init-073/result.json', 'original-init-074/result.json'),
                 ('GRAPHICS073_', 'GRAPHICS074_'), ('ORIGINAL_INIT073_', 'ORIGINAL_INIT074_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
anchor = "add('graphics-init.cfg',stat.S_IFREG|0o444,Path(prep['files']['graphics-init.cfg']['path']).read_bytes())"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, '''ashmem=json.loads((root/'original-graphics-ashmem-004/result.json').read_text())
assert ashmem['kernel_sha256']=='a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136'
assert ashmem['module_sha256']=='951e58dceffa3bc00abeab793b4dcbd8d846644d08524e5128aaff7f2c6c493d'
module_bytes=Path(ashmem['module_path']).read_bytes()
assert len(module_bytes)==ashmem['module_bytes'] and hashlib.sha256(module_bytes).hexdigest()==ashmem['module_sha256']
add('graphics-ashmem.ko',stat.S_IFREG|0o444,module_bytes)
''' + anchor)
compile(payload, 'original-real-ashmem-074-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)

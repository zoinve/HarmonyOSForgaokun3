"""Inspect the supplied original memory-service initialization offline."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
OUT = ROOT / 'reports/memmgr-initialization-audit-109'


if __name__ == '__main__':
    assert not OUT.exists()
    source = '/system/lib64/libmemmgrservice.z.so'
    extracted = subprocess.run(['/usr/sbin/debugfs', '-R', 'cat ' + source, IMAGE],
                               capture_output=True, check=True)
    data = extracted.stdout
    assert data.startswith(b'\x7fELF') and b'File not found' not in extracted.stderr
    OUT.mkdir()
    library = OUT / Path(source).name
    library.open('xb').write(data)
    symbols = subprocess.check_output(['aarch64-linux-gnu-readelf', '-Ws', '--wide', str(library)])
    readable = subprocess.check_output(['aarch64-linux-gnu-c++filt'], input=symbols)
    (OUT / 'symbols.txt').open('xb').write(readable)
    strings = subprocess.check_output(['strings', '-a', str(library)])
    (OUT / 'strings.txt').open('xb').write(strings)
    selected = [line.decode(errors='replace') for line in readable.splitlines()
                if any(token in line for token in
                       (b'MemMgrService::', b'MemoryManagerService::', b'OnStart(', b'Publish(', b'Init('))]
    result = dict(source=source, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                  initialization_symbols=selected, read_only_debugfs=True,
                  original_image_mounted=False, original_binary_modified=False,
                  target_boot_performed=False, service_failure_cause_proven=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

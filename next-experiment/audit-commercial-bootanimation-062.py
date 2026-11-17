"""Read-only bootanimation lifecycle audit; no deployment or operational boot."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-bootanimation-audit-062'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    paths = ['/system/bin/bootanimation', '/system/etc/init/bootanimation.cfg',
             '/system/etc/param/bootanimation.para']
    blobs = {}
    for origin in paths:
        proc = subprocess.run(['debugfs', '-R', 'cat ' + origin, str(IMAGE)],
                              capture_output=True, check=True)
        assert proc.stdout, (origin, proc.stderr)
        blobs[origin] = proc.stdout
    assert blobs[paths[0]].startswith(b'\x7fELF')
    config = json.loads(blobs[paths[1]])
    OUT.mkdir()
    manifest = []
    for origin, data in blobs.items():
        name = Path(origin).name
        (OUT / name).open('xb').write(data)
        manifest.append(dict(image=str(IMAGE), origin=origin, name=name,
                             size=len(data), sha256=hashlib.sha256(data).hexdigest()))
    binary = OUT / 'bootanimation'
    symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '-C', str(binary)], text=True)
    (OUT / 'symbols.txt').open('x').write(symbols)
    disassembly = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle', str(binary)], text=True)
    (OUT / 'all.asm').open('x').write(disassembly)
    strings = subprocess.check_output(['strings', '-t', 'x', str(binary)], text=True)
    (OUT / 'strings.txt').open('x').write(strings)
    sections = re.split(r'(?=^[0-9a-f]+ <)', disassembly, flags=re.MULTILINE)
    selected = ''.join(s for s in sections if any(k in s.split('\n', 1)[0] for k in
        ['main>', 'BootAnimation', 'BootCompatible', 'BootStrategy', 'BootPicture', 'BootVideo']))
    (OUT / 'lifecycle.asm').open('x').write(selected)
    result = dict(files=manifest, service_config=config, read_only_image_access=True,
                  images_modified=False, operational_boot_performed=False,
                  lifecycle_cause_proven=False, desktop_verified=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

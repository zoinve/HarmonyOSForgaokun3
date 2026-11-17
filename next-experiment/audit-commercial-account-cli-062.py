"""Inspect original account CLI without executing it or changing account state."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-account-cli-062'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    data = subprocess.check_output(['debugfs', '-R', 'cat /system/bin/acm', str(IMAGE)], stderr=subprocess.DEVNULL)
    assert data.startswith(b'\x7fELF')
    OUT.mkdir()
    binary = OUT / 'acm'
    binary.open('xb').write(data)
    for name, command in [('strings.txt', ['strings', '-t', 'x']),
                          ('symbols.txt', ['aarch64-linux-gnu-nm', '-D', '-C']),
                          ('all.asm', ['llvm-objdump-19', '-d', '--demangle'])]:
        text = subprocess.check_output(command + [str(binary)], text=True)
        (OUT / name).open('x').write(text)
    result = dict(origin='/system/bin/acm', image=str(IMAGE), bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(), account_cli_executed=False,
        account_state_modified=False, images_modified=False, desktop_verified=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

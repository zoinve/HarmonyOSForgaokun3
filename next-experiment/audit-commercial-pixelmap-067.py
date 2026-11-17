"""Inspect original PixelMap error handling; never run or patch the library."""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path(__file__).resolve().parents[1]
OUT = B / 'reports/commercial-pixelmap-audit-067'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
SOURCE = '/system/lib64/platformsdk/libimage_native.z.so'

if __name__ == '__main__':
    OUT.mkdir(exist_ok=False)
    binary = subprocess.check_output(['debugfs', '-R', 'cat ' + SOURCE, str(IMAGE)], stderr=subprocess.DEVNULL)
    assert binary[:6] == b'\x7fELF\x02\x01'
    message = b'set ashmem name failed'
    assert message in binary
    target = OUT / 'libimage_native.z.so'
    target.open('xb').write(binary)
    symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '-C', '--defined-only', str(target)])
    (OUT / 'symbols.txt').open('xb').write(symbols)
    assembly = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle', str(target)])
    (OUT / 'disassembly.txt').open('xb').write(assembly)
    result = dict(original_path=SOURCE, original_sha256=hashlib.sha256(binary).hexdigest(),
                  warning_file_offset=hex(binary.index(message)),
                  original_image_modified=False, code_executed=False, code_patched=False,
                  warning_is_root_cause_proven=False)
    (OUT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

"""Static original resource-manager inspection; no live object reads or patch."""
from pathlib import Path
import hashlib
import json
import subprocess

b = Path(__file__).resolve().parent
out = b.parent / 'reports/commercial-rawfile-path-audit-069'
image = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
source = '/system/lib64/platformsdk/libglobal_resmgr.z.so'
out.mkdir()
data = subprocess.check_output(['debugfs', '-R', 'cat '+source, str(image)], stderr=subprocess.DEVNULL)
assert data[:6] == b'\x7fELF\x02\x01'
target = out / Path(source).name
target.open('xb').write(data)
symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '-C', '--defined-only', str(target)])
(out / 'symbols.txt').open('xb').write(symbols)
assembly = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle', str(target)])
(out / 'disassembly.txt').open('xb').write(assembly)
messages = ['FindRawFile path to realpath error', 'index path format error',
            '/resources/', 'rawfile/', 'GetRawFilePathByName']
result = dict(original_path=source, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
    symbols=[line for line in symbols.decode().splitlines() if any(part in line for part in (
        'FindRawFile', 'GetRawFilePath', 'GetRawFileDescriptor', 'GetRawFileFromHap', 'GetRawFileData'))],
    string_file_offsets={text:hex(data.find(text.encode())) if text.encode() in data else None for text in messages},
    original_image_written=False, library_executed=False, library_patched=False,
    live_private_object_read=False, operational_boot_performed=False)
with (out / 'result.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))

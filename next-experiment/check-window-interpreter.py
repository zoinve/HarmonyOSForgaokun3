"""Check executable ELF interpreters in an actual diskless newc archive."""
import gzip
import struct
import sys
from pathlib import Path

raw = gzip.decompress(Path(sys.argv[1]).read_bytes())
entries = {}
pos = 0
while True:
    header = raw[pos:pos + 110]
    assert header[:6] == b'070701'
    mode = int(header[14:22], 16)
    size = int(header[54:62], 16)
    namesize = int(header[94:102], 16)
    name = raw[pos + 110:pos + 109 + namesize].decode()
    start = (pos + 110 + namesize + 3) & ~3
    pos = (start + size + 3) & ~3
    if name == 'TRAILER!!!':
        break
    assert name not in entries
    entries[name] = (mode, raw[start:start + size])
mode, elf = entries['gpu-userspace-probe']
assert mode & 0o111 and elf[:6] == b'\x7fELF\x02\x01'
offset = struct.unpack_from('<Q', elf, 32)[0]
stride, count = struct.unpack_from('<HH', elf, 54)
for i in range(count):
    ph = offset + stride * i
    if struct.unpack_from('<I', elf, ph)[0] == 3:
        start = struct.unpack_from('<Q', elf, ph + 8)[0]
        length = struct.unpack_from('<Q', elf, ph + 32)[0]
        interpreter = elf[start:start + length].rstrip(b'\0').decode().lstrip('/')
        assert entries[interpreter][0] & 0o111, f'ELF interpreter is not executable: {interpreter}'
        print('PASS: executable probe and ELF interpreter', interpreter)
        break
else:
    raise AssertionError('Fixture has no PT_INTERP')

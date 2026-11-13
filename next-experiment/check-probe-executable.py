"""Validate actual diagnostic initramfs executable permissions."""
import gzip
import sys
from pathlib import Path

raw = gzip.decompress(Path(sys.argv[1]).read_bytes())
offset = 0
found = set()
while True:
    header = raw[offset:offset + 110]
    assert header[:6] == b'070701'
    fields = [int(header[i:i + 8], 16) for i in range(6, 110, 8)]
    mode, size, namesize = fields[1], fields[6], fields[11]
    name = raw[offset + 110:offset + 110 + namesize]
    assert name.endswith(b'\0')
    name = name[:-1].decode()
    offset = (offset + 110 + namesize + 3) & ~3
    if name == 'TRAILER!!!':
        break
    if name in ('init', 'gpu883-libs/gpu-frontend-probe'):
        assert mode & 0o111 == 0o111, f'{name} not executable: {oct(mode)}'
        found.add(name)
    offset = (offset + size + 3) & ~3
assert len(found) == 2, found
print('PASS: init and standalone GPU diagnostic are executable in actual archive')

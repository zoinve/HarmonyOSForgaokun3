"""Derive 926 from immutable 925, changing only the interpreter mode."""
import gzip
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent
source = base / 'official-window-probe-925/initramfs.cpio.gz'
original = source.read_bytes()
assert hashlib.sha256(original).hexdigest() == '67342ca81e0e8ee3f215a12d24652ba317a64f957062c8e3232e7d566a1bb26d'
raw = gzip.decompress(original)
updated = bytearray(raw)
pos = 0
changed = []
while True:
    header = raw[pos:pos + 110]
    assert header[:6] == b'070701'
    size, namesize = int(header[54:62], 16), int(header[94:102], 16)
    name = raw[pos + 110:pos + 109 + namesize].decode()
    if name == 'lib/ld-musl-aarch64.so.1':
        assert header[14:22] == b'00008124'  # regular 0444
        updated[pos + 14:pos + 22] = b'000081ed'  # regular 0755
        changed.append(pos + 14)
    start = (pos + 110 + namesize + 3) & ~3
    pos = (start + size + 3) & ~3
    if name == 'TRAILER!!!':
        break
assert len(changed) == 1
index = changed[0]
assert updated[:index] == raw[:index] and updated[index + 8:] == raw[index + 8:]
archive = gzip.compress(updated, mtime=0)
out = base / 'official-window-probe-926'
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
manifest = dict(source_sha256=hashlib.sha256(original).hexdigest(),
                initrd_sha256=hashlib.sha256(archive).hexdigest(),
                changed_mode={'lib/ld-musl-aarch64.so.1': ['100444', '100755']},
                all_payload_bytes_unchanged=True, disks_attached=0, desktop_verified=False)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))

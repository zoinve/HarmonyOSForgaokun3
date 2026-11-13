"""Throwaway compatibility payload: preserve official init, add its own fstab in RAM."""
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent
source = Path('D:/Download/pc_all_arm/ramdisk.img')
out = base / 'official-arm-mount-921'
assert not out.exists(), 'Never overwrite a completed payload'
result = subprocess.run(
    ['wsl', '-d', 'Debian', '--', 'debugfs', '-R',
     'cat /etc/fstab.hmos.emulator', '/mnt/d/Download/pc_all_arm/vendor.img'],
    capture_output=True, check=True)
fstab = result.stdout
assert b'/dev/block/vda' in fstab and b'/dev/block/vdd' in fstab
assert b'wait,required' in fstab and b'/usr' in fstab
original = source.read_bytes()
raw = gzip.decompress(original)
pos = 0
names = []
while True:
    start = pos
    header = raw[pos:pos + 110]
    assert header[:6] == b'070701'
    fields = [int(header[6 + i * 8:14 + i * 8], 16) for i in range(13)]
    name = raw[pos + 110:pos + 110 + fields[11] - 1].decode()
    data = (pos + 110 + fields[11] + 3) & ~3
    pos = (data + fields[6] + 3) & ~3
    if name == 'TRAILER!!!':
        break
    names.append(name)
assert 'etc' in names and 'etc/fstab.required' not in names


def entry(name, contents, mode, inode):
    encoded = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(contents), 0, 0, 0, 0, len(encoded), 0]
    block = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + encoded
    block += b'\0' * (-len(block) % 4)
    block += contents
    return block + b'\0' * (-len(block) % 4)


new = raw[:start] + entry('etc/fstab.required', fstab, 0o100644, 900001)
new += entry('TRAILER!!!', b'', 0, 900002)
assert new[:start] == raw[:start]  # Every original file, including init, is unchanged.
payload = gzip.compress(new, mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(payload)
(out / 'fstab.required').write_bytes(fstab)
(out / 'manifest.json').write_text(json.dumps({
    'source': str(source),
    'original_ramdisk_sha256': hashlib.sha256(original).hexdigest(),
    'initramfs_sha256': hashlib.sha256(payload).hexdigest(),
    'added_file': 'etc/fstab.required',
    'fstab_source': 'Original vendor.img /etc/fstab.hmos.emulator, unchanged bytes',
    'fstab_sha256': hashlib.sha256(fstab).hexdigest(),
    'original_archive_prefix_unchanged': True,
    'original_files': len(names),
    'desktop_verified': False,
}, indent=2), encoding='utf-8')
print((out / 'manifest.json').read_text())

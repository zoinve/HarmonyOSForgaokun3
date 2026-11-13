"""Diskless compatibility probe: replace only the runtime loader in probe 883."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
out = base / 'official-gpu-probe-924'
assert not out.exists(), 'Never overwrite a numbered probe'
source = base / 'gpu-runtime-883/gpu-userspace-probe.cpio.gz'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'eac2bdbdba355034b00af79d28beacd5cf4e69cc397980fce545376db36c24c4'
out.mkdir()
loader = out / 'official-loader.so'
wsl_path = '/mnt/' + loader.drive[0].lower() + loader.as_posix()[2:]
subprocess.run(['wsl', '-d', 'Debian', '--', 'debugfs', '-R',
                'dump /system/lib/ld-musl-aarch64.so.1 ' + wsl_path,
                '/mnt/d/Download/pc_all_arm/system.img'], check=True)
replacement = loader.read_bytes()
assert replacement[:4] == b'\x7fELF' and len(replacement) == 2246112
raw = gzip.decompress(source.read_bytes())
chunks, changed, rows = [], [], []
pos = 0
while True:
    start = pos
    header = raw[pos:pos + 110]
    assert header[:6] == b'070701'
    size = int(header[54:62], 16)
    namesize = int(header[94:102], 16)
    namebytes = raw[pos + 110:pos + 110 + namesize]
    assert namebytes[-1:] == b'\0'
    name = namebytes[:-1].decode()
    body_start = (pos + 110 + namesize + 3) & ~3
    body = raw[body_start:body_start + size]
    pos = (body_start + size + 3) & ~3
    if name == 'lib/ld-musl-aarch64.so.1':
        changed.append(name)
        updated = header[:54] + f'{len(replacement):08x}'.encode() + header[62:]
        chunk = updated + raw[start + 110:body_start] + replacement
        chunk += b'\0' * (-len(chunk) % 4)
        chunks.append(chunk)
        body = replacement
    else:
        chunks.append(raw[start:pos])
    rows.append({'path': name, 'sha256': hashlib.sha256(body).hexdigest()})
    if name == 'TRAILER!!!':
        break
assert changed == ['lib/ld-musl-aarch64.so.1']
archive = gzip.compress(b''.join(chunks), mtime=0)
(out / 'initramfs.cpio.gz').write_bytes(archive)
manifest = dict(changed_entries=changed, disks_attached=0, desktop_verified=False,
                loader_sha256=hashlib.sha256(replacement).hexdigest(),
                initrd_sha256=hashlib.sha256(archive).hexdigest(), files=rows)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))

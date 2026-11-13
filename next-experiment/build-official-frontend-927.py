"""Diskless frontend compatibility fixture; SDK images are strictly read-only.

Run under WSL. Derives a new archive, never edits completed experiments.
"""
from pathlib import Path
import gzip
import hashlib
import json
import posixpath
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
out = base / 'official-frontend-probe-927'
work = Path('/home/zoinve/harmony-virgl-883/official-frontend-probe-927')
assert not out.exists() and not work.exists()
source = base / 'official-window-probe-926/initramfs.cpio.gz'
compressed = source.read_bytes()
assert hashlib.sha256(compressed).hexdigest() == 'a0b02e37276a0d6751a7d902b4898e24592f6213a87a0542022fd63ac393695b'
raw = gzip.decompress(compressed)
entries = {}
pos = 0
while True:
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + ns].decode()
    start = (pos + 110 + ns + 3) & ~3
    pos = (start + size + 3) & ~3
    if name == 'TRAILER!!!':
        break
    assert name not in entries
    entries[name] = (int(h[14:22], 16), raw[start:start + size])

# Change only this diagnostic executable's DT_NEEDED names, not official ELF files.
mode, probe = entries['gpu-userspace-probe']
for old, new in [(b'libEGL_impl.so\0', b'libEGL.so\0'),
                 (b'libGLESv2.so.2\0', b'libGLESv3.so\0')]:
    assert probe.count(old) == 1
    probe = probe.replace(old, new.ljust(len(old), b'\0'))
entries['gpu-userspace-probe'] = mode, probe

work.mkdir()
image = '/mnt/d/Download/pc_all_arm/system.img'
folders = ['/system/lib64', '/system/lib64/chipset-sdk-sp',
           '/system/lib64/platformsdk', '/system/lib64/chipset-pub-sdk',
           '/system/lib64/chipset-sdk', '/system/lib64/ndk']
private = 'system/lib64/lab-softpipe-167/'
queue, seen, extracted = ['libEGL.so', 'libGLESv3.so'], set(), []
while queue:
    name = queue.pop()
    if name in seen or name == 'libc.so':
        continue
    seen.add(name)
    for folder in folders:
        candidate = folder + '/' + name
        for _ in range(12):
            stat = subprocess.run(['debugfs', '-R', 'stat ' + candidate, image],
                                  text=True, capture_output=True, check=True).stdout
            match = re.search(r'Fast link dest: "(.*?)"', stat)
            if not match:
                break
            candidate = posixpath.normpath(posixpath.join(posixpath.dirname(candidate), match[1]))
        if 'Type: regular' in stat:
            break
    else:
        raise AssertionError(('unresolved official dependency', name))
    dest = work / name
    subprocess.run(['debugfs', '-R', f'dump {candidate} {dest}', image],
                   check=True, capture_output=True)
    body = dest.read_bytes()
    assert body.startswith(b'\x7fELF')
    entries[private + name] = 0o100444, body
    dynamic = subprocess.check_output(['readelf', '-dW', str(dest)], text=True)
    queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic))
    extracted.append(dict(name=name, source=candidate, sha256=hashlib.sha256(body).hexdigest()))
    print('OFFICIAL', name, len(body), flush=True)

# The original frontend may resolve its driver and GLES dispatcher by absolute path.
for name, target in [('libEGL_impl.so', 'libEGL_impl.so'),
                     ('libGLESv1_impl.so', 'libGLESv2.so.2'),
                     ('libGLESv2_impl.so', 'libGLESv2.so.2'),
                     ('libGLESv3_impl.so', 'libGLESv2.so.2'),
                     ('libGLESv3.so', 'libGLESv3.so')]:
    key = 'system/lib64/' + name
    assert key not in entries
    entries[key] = 0o120777, ('lab-softpipe-167/' + target).encode()

chunks = []
for inode, (name, (mode, body)) in enumerate(sorted(entries.items()), 1):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(nb), 0]
    head = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    chunks.append(head + b'\0' * (-len(head) % 4) + body + b'\0' * (-len(body) % 4))
nb = b'TRAILER!!!\0'
values = [len(entries) + 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(nb), 0]
tail = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
chunks.append(tail + b'\0' * (-len(tail) % 4))
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(
    initrd_sha256=hashlib.sha256(archive).hexdigest(), official_libraries=extracted,
    fixture_needed=['libEGL.so', 'libGLESv3.so'], disks_attached=0,
    desktop_verified=False, official_images_modified=False), indent=2))
print('BUILT', hashlib.sha256(archive).hexdigest(), 'not executed')

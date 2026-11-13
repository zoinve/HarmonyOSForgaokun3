"""Add unchanged original vendor plugins to the diskless 936 diagnostic."""
from pathlib import Path
import gzip
import hashlib
import json
import posixpath
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-vendor-937'
work = root / 'native-vendor-937'
assert not out.exists() and not work.exists()
old = (base / 'official-native-loader-936/initramfs.cpio.gz').read_bytes()
assert hashlib.sha256(old).hexdigest() == 'cb6c7221b357362dd341af97d59e59e72004257995ab58eef0ddbc0a7ba9b900'
raw = gzip.decompress(old)
entries, pos = {}, 0
while True:
    begin = pos
    h = raw[pos:pos+110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos+110:pos+109+ns].decode()
    start = (pos+110+ns+3) & ~3
    pos = (start+size+3) & ~3
    if name == 'TRAILER!!!':
        prefix = raw[:begin]
        break
    assert name not in entries
    entries[name] = raw[start:start+size]
work.mkdir()
vendor = '/mnt/d/Download/pc_all_arm/vendor.img'
system = '/mnt/d/Download/pc_all_arm/system.img'
private = 'system/lib64/lab-softpipe-167/'
plugins = [
    '/lib64/passthrough/libmapper_service_1.0.z.so',
    '/lib64/passthrough/libmapper_service_1.2.z.so',
    '/lib64/passthrough/libmapper_service_1.3.z.so',
    '/lib64/passthrough/libmetadata_service_1.1.z.so',
    '/lib64/liballocator_service_1.0.z.so',
    '/lib64/liballocator_service_1.4.z.so',
    '/lib64/libdisplay_buffer_vdi_impl.z.so',
    '/lib64/libdisplay_buffer_vendor.z.so',
]
added, sources, queue = {}, [], []

def extract(image, original, target):
    assert target not in entries and target not in added, target
    dest = work / ('file-' + str(len(sources)))
    subprocess.run(['debugfs', '-R', f'dump {original} {dest}', image],
                   check=True, capture_output=True)
    body = dest.read_bytes()
    assert body[:4] == b'\x7fELF', original
    added[target] = (0o100444, body)
    sources.append(dict(image=image, original=original, target=target,
                        sha256=hashlib.sha256(body).hexdigest()))
    queue.append((dest, target))
    return body

for original in plugins:
    target = 'vendor' + original
    body = extract(vendor, original, target)
    # Normal dependent and dlopen lookup in this isolated fixture's private path.
    alias = private + posixpath.basename(original)
    assert alias not in entries and alias not in added
    added[alias] = (0o100444, body)

seen = set()
while queue:
    dest, target = queue.pop()
    if target in seen:
        continue
    seen.add(target)
    dynamic = subprocess.check_output(['readelf', '-dW', str(dest)], text=True)
    for needed in re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic):
        if needed == 'libc.so' or private + needed in entries or private + needed in added:
            continue
        found = False
        for image, folders in [(vendor, ['/lib64', '/lib64/passthrough']),
                               (system, ['/system/lib64', '/system/lib64/chipset-sdk-sp',
                                         '/system/lib64/platformsdk', '/system/lib64/chipset-pub-sdk',
                                         '/system/lib64/chipset-sdk', '/system/lib64/ndk'])]:
            for folder in folders:
                candidate = folder + '/' + needed
                for _ in range(8):
                    stat = subprocess.run(['debugfs', '-R', 'stat ' + candidate, image],
                                          capture_output=True, text=True).stdout
                    link = re.search(r'Fast link dest: "(.*?)"', stat)
                    if not link:
                        break
                    candidate = posixpath.normpath(posixpath.join(posixpath.dirname(candidate), link[1]))
                if 'Type: regular' in stat:
                    extract(image, candidate, private + needed)
                    found = True
                    break
            if found:
                break
        assert found, ('missing original dependency', needed)

def entry(name, mode, body, inode):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(nb), 0]
    head = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    head += b'\0' * (-len(head) % 4)
    return head + body + b'\0' * (-len(body) % 4)

for directory in ['vendor', 'vendor/lib64', 'vendor/lib64/passthrough']:
    if directory not in entries:
        added[directory] = (0o40755, b'')
chunks = [prefix]
for inode, (name, (mode, body)) in enumerate(sorted(added.items()), 900000):
    chunks.append(entry(name, mode, body, inode))
chunks.append(entry('TRAILER!!!', 0, b'', 990000))
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
manifest = dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
                original_entries_unchanged=True, added_entries=list(added), sources=sources,
                disks_attached=0, desktop_verified=False)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('BUILT', manifest['initrd_sha256'], 'unchanged original vendor plugins', len(sources))

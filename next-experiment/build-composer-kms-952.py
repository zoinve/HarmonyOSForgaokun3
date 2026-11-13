"""Fresh diskless real DMA-BUF/KMS diagnostic, based on immutable official 946."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
ref = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports')
out, work = base / 'official-composer-kms-952', root / 'composer-kms-952-build2'
assert not out.exists() and not work.exists()
parent = base / 'official-skia-context-946/initramfs.cpio.gz'
assert hashlib.sha256(parent.read_bytes()).hexdigest() == '19df8a67aa18cd9ba4e6a63ce4c2602034768e892d240b42c55e3d2fbfbc1547'
raw = gzip.decompress(parent.read_bytes())
entries, pos = {}, 0
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
    entries[name] = int(h[14:22], 16), raw[start:start + size]
work.mkdir()
prefix = root / 'prefix/system'
libs = prefix / 'lib64/lab-virgl883'
tool = root / 'window-bridge/toolchain'
include = ref / 'graphics/include'
common = ['-I' + str(include), '-I' + str(prefix / 'include'), '-I' + str(prefix / 'include/libdrm')]
subprocess.run([str(tool / 'ohos-cc'), '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror',
                *common, '-c', str(ref / 'graphics/drm_device.c'), '-o', str(work / 'drm_device.o')], check=True)
subprocess.run([str(tool / 'ohos-platform-cxx'), '-shared', '-fPIC', '-O2', '-std=c++17',
                '-Wall', '-Wextra', *common, str(ref / 'graphics/composer.cpp'), str(work / 'drm_device.o'),
                '-L' + str(libs), '-ldrm', '-Wl,--no-undefined,-soname,libdisplay_composer_vdi_impl.z.so',
                '-Wl,-rpath,/system/lib64/lab-softpipe-167', '-o', str(work / 'libdisplay_composer_vdi_impl.z.so')], check=True)
exports = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '--defined-only', str(work / 'libdisplay_composer_vdi_impl.z.so')], text=True)
slots = json.loads((base.parent / 'reports/composer-sdk7-loader-slots-951.json').read_text())
missing = [r['name'] for r in slots if r['mandatory'] and not re.search(r'\b' + r['name'] + r'$', exports, re.M)]
assert not missing, missing
source = (ref / 'tests/composer-probe.cpp').read_text()
source = source.replace('/vendor/lib64/aurora-graphics/', '/vendor/lib64/')
source = source.replace('    setbuf(stdout, nullptr); alarm(45);',
                        '    setbuf(stdout, nullptr); alarm(45);\n'
                        '    static_assert(sizeof(Capability)==80 && sizeof(Property)==40 && sizeof(Mode)==16);\n'
                        '    static_assert(sizeof(AuroraComposer::LayerInfo)==20 && sizeof(AuroraComposer::Alpha)==5);')
(work / 'probe.cpp').write_text(source)
subprocess.run([str(tool / 'ohos-platform-cxx'), '-O2', '-std=c++17', '-Wall', '-Wextra',
                '-I' + str(include), str(work / 'probe.cpp'), '-ldl',
                '-Wl,-rpath,/system/lib64/lab-softpipe-167', '-o', str(work / 'probe')], check=True)
entries['gpu-userspace-probe'] = 0o100755, (work / 'probe').read_bytes()
body = (work / 'libdisplay_composer_vdi_impl.z.so').read_bytes()
entries['vendor/lib64/libdisplay_composer_vdi_impl.z.so'] = 0o100444, body
entries['system/lib64/lab-softpipe-167/libdisplay_composer_vdi_impl.z.so'] = 0o100444, body

def entry(name, mode, data, inode):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(nb), 0]
    head = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    return head + b'\0' * (-len(head) % 4) + data + b'\0' * (-len(data) % 4)

archive = gzip.compress(b''.join(entry(n, m, b, i) for i, (n, (m, b)) in enumerate(sorted(entries.items()), 1)) +
                        entry('TRAILER!!!', 0, b'', len(entries) + 1), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'exports.txt').write_text(exports)
(out / 'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(), mandatory_exports_verified=True,
    mandatory_count=sum(r['mandatory'] for r in slots), disks_attached=0, desktop_verified=False,
    purpose='Real DMA-BUF and KMS commit diagnostic, not a desktop'), indent=2))
print((out / 'manifest.json').read_text())

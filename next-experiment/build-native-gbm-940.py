"""Diskless GBM VDI integration; official mapper and consumer remain unchanged."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

local = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = local / 'official-native-gbm-940'
work = root / 'native-gbm-940'
assert not out.exists() and not work.exists()
source_archive = local / 'official-native-alloc-handle-939/initramfs.cpio.gz'
assert hashlib.sha256(source_archive.read_bytes()).hexdigest() == 'b302e513c2daa87f7075e6169a1888a5e446ad8ec6de984b7516251fc6d294ce'
raw = gzip.decompress(source_archive.read_bytes())
old = root / 'gbm-vdi-905'
source = (old / 'buffer_vdi.cpp').read_text()
# Regression gate: the previous GBM implementation inherited NOT_SUPPORT.
assert 'int32_t IsSupportAllocPassthrough(' not in source
anchor = '    int32_t IsSupportedAlloc('
assert source.count(anchor) == 1
source = source.replace(anchor, '''    int32_t IsSupportAllocPassthrough(const BufferAllocInfo &info) const override
    {
        if (!supported(info.width, info.height, info.format, info.usage) || !device())
            return NOT_SUPPORT;
        return gbm_device_is_format_supported(gbm_, fourcc(info.format),
            GBM_BO_USE_RENDERING | GBM_BO_USE_LINEAR) ? 0 : NOT_SUPPORT;
    }

''' + anchor)
work.mkdir()
(work / 'buffer_vdi.cpp').write_text(source)
prefix = root / 'prefix/system'
libs = prefix / 'lib64/lab-virgl883'
cc = root / 'window-bridge/toolchain/ohos-platform-cxx'
cmd = [str(cc), '-O2', '-std=c++17', '-Wall', '-Wextra', '-shared', '-fPIC',
       '-isystem', str(old / 'include'), '-I' + str(old),
       '-I' + str(prefix / 'include'), '-I' + str(prefix / 'include/libdrm'),
       str(work / 'buffer_vdi.cpp'), str(old / 'drm_device.o'),
       '-L' + str(libs), '-lgbm', '-ldrm',
       str(root / 'official-frontend-probe-927/libbuffer_handle.z.so'),
       '-Wl,--no-undefined,-soname,libdisplay_buffer_vdi_impl.z.so',
       '-Wl,-rpath,/system/lib64/lab-softpipe-167',
       '-o', str(work / 'libdisplay_buffer_vdi_impl.z.so')]
subprocess.run(cmd, check=True)
body = (work / 'libdisplay_buffer_vdi_impl.z.so').read_bytes()
targets = {'vendor/lib64/libdisplay_buffer_vdi_impl.z.so',
           'system/lib64/lab-softpipe-167/libdisplay_buffer_vdi_impl.z.so'}
chunks, changes = [], []
pos = 0
while True:
    start = pos
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, namesize = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + namesize].decode()
    data = (pos + 110 + namesize + 3) & ~3
    pos = (data + size + 3) & ~3
    if name in targets:
        chunk = h[:54] + f'{len(body):08x}'.encode() + h[62:] + raw[start + 110:data] + body
        chunk += b'\0' * (-len(chunk) % 4)
        chunks.append(chunk)
        changes.append(name)
    else:
        chunks.append(raw[start:pos])
    if name == 'TRAILER!!!':
        break
assert set(changes) == targets
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
manifest = dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
                changed_entries=changes, adapter_sha256=hashlib.sha256(body).hexdigest(),
                disks_attached=0, desktop_verified=False,
                official_mapper_modified=False, original_images_modified=False)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))

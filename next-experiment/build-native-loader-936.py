"""Trace HDI plugin loading from the disposable fixture, forwarding unchanged."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-loader-936'
work = root / 'native-loader-936'
assert not out.exists() and not work.exists()
old = (base / 'official-native-trace-935/initramfs.cpio.gz').read_bytes()
assert hashlib.sha256(old).hexdigest() == '1c4a2cd86e20b006f2c0ff948ca3d2cb9c47726b8302100dab68c3e34d105977'
source = (root / 'native-trace-935/probe.c').read_text()
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
__attribute__((visibility("default")))
void *LoadHdiImpl(const char *descriptor, const char *service)
{
    typedef void *(*Loader)(const char *, const char *);
    Loader real = (Loader)dlsym(RTLD_NEXT, "LoadHdiImpl");
    printf("NATIVE936_LOAD descriptor=%s service=%s real=%p\n",
        descriptor ? descriptor : "(null)", service ? service : "(null)", (void *)real);
    if (!real) { fprintf(stderr, "NATIVE936 missing real loader: %s\n", dlerror()); exit(126); }
    void *result = real(descriptor, service);
    printf("NATIVE936_LOAD_RESULT service=%s result=%p\n", service ? service : "(null)", result);
    return result;
}
''' + anchor)
source = source.replace('NATIVE935_', 'NATIVE936_')
work.mkdir()
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
    '-I' + str(root / 'prefix/include'), str(work / 'probe.c'), str(libs / 'libEGL.so'),
    str(libs / 'libGLESv3.so'), '-ldl', '-Wl,--export-dynamic',
    '-Wl,-rpath,/system/lib64/lab-softpipe-167', '-Wl,-rpath-link,' + str(libs),
    '-o', str(work / 'probe')], check=True)
raw = gzip.decompress(old)
chunks, pos, changed = [], 0, []
while True:
    begin = pos
    h = raw[pos:pos+110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos+110:pos+109+ns].decode()
    start = (pos+110+ns+3) & ~3
    pos = (start+size+3) & ~3
    if name == 'gpu-userspace-probe':
        body = (work / 'probe').read_bytes()
        chunk = h[:54] + f'{len(body):08x}'.encode() + h[62:] + raw[begin+110:start] + body
        chunks.append(chunk + b'\0' * (-len(chunk) % 4))
        changed.append(name)
    else:
        chunks.append(raw[begin:pos])
    if name == 'TRAILER!!!': break
assert changed == ['gpu-userspace-probe']
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    changed_entries=changed, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

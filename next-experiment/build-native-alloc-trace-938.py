"""Trace real mapper allocation calls; never replace their results or SDK DSOs."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-alloc-trace-938'
work = root / 'native-alloc-trace-938'
assert not out.exists() and not work.exists()
old = (base / 'official-native-vendor-937/initramfs.cpio.gz').read_bytes()
assert hashlib.sha256(old).hexdigest() == '5933fad14ba4495d2cf29265a0a588e6213d10c2b7cc66758edbae4a5daa7145'
source = (root / 'native-loader-936/probe.c').read_text()
symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', str(root / 'vendor-allocator-inspect-936/libmapper_service_1.0.z.so')], text=True)
wrappers = []
for method in ['IsSupportAllocPassthrough', 'AllocMem', 'ReAllocMem']:
    matches = [line.split()[-1] for line in symbols.splitlines()
               if ' T ' in line and ('13MapperService' + str(len(method)) + method) in line]
    assert len(matches) == 1, (method, matches)
    symbol = matches[0]
    count = 2 if method == 'IsSupportAllocPassthrough' else (3 if method == 'AllocMem' else 4)
    args = ', '.join('void *a%d' % i for i in range(count))
    types = ', '.join(['void *'] * count)
    forwarded = ', '.join('a%d' % i for i in range(count))
    wrappers.append(f'''
__attribute__((visibility("default"))) int trace_{method}({args}) __asm__("{symbol}");
int trace_{method}({args}) {{
    typedef int (*Fn)({types});
    Fn real = (Fn)dlsym(RTLD_NEXT, "{symbol}");
    if (!real) {{ fprintf(stderr, "NATIVE938_MISSING {method} %s\\n", dlerror()); exit(126); }}
    printf("NATIVE938_ENTER {method}\\n");
    int rc = real({forwarded});
    printf("NATIVE938_RETURN {method} rc=%d\\n", rc);
    return rc;
}}
''')
assert source.count('int main(void)') == 1
source = source.replace('int main(void)', '\n'.join(wrappers) + '\nint main(void)')
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
    changed_entries=changed, forwarded_mapper_methods=True, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

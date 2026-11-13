"""Diskless comparison: official eglGetDisplay instead of extension lookup."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-frontend-probe-930'
work = root / 'frontend-default-930'
assert not out.exists() and not work.exists()
work.mkdir()
source = (base / 'gpu-userspace-probe.c').read_text()
start = source.index('    PFNEGLQUERYDEVICESEXTPROC query')
end = source.index('    EGLint major, minor;', start)
source = source[:start] + '''    EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    require(display != EGL_NO_DISPLAY, "default display");
    printf("FRONTEND930_DISPLAY value=%p\\n", (void *)display);
    EGLint count = 0;
''' + source[end:]
source = source.replace('GPU883_', 'FRONTEND930_')
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(libs / 'libEGL.so'), str(libs / 'libGLESv3.so'),
                '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
original = base / 'official-frontend-probe-929/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == 'b5376157ecf340be89ba4e93a56dd0a541d9996a95b661b8e5c043b08f073478'
raw = gzip.decompress(original.read_bytes())
chunks, changed, pos = [], [], 0
while True:
    start = pos
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + ns].decode()
    data = (pos + 110 + ns + 3) & ~3
    pos = (data + size + 3) & ~3
    if name == 'gpu-userspace-probe':
        body = (work / 'probe').read_bytes()
        chunk = h[:54] + f'{len(body):08x}'.encode() + h[62:] + raw[start + 110:data] + body
        chunks.append(chunk + b'\0' * (-len(chunk) % 4))
        changed.append(name)
    else:
        chunks.append(raw[start:pos])
    if name == 'TRAILER!!!':
        break
assert changed == ['gpu-userspace-probe']
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(
    initrd_sha256=hashlib.sha256(archive).hexdigest(), changed_entries=changed,
    official_libraries_unchanged=True, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

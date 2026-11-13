"""Diagnostic-only fixture: distinguish config API status from match count."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-frontend-probe-931'
work = root / 'frontend-config-931'
assert not out.exists() and not work.exists()
work.mkdir()
source = (root / 'frontend-default-930/probe.c').read_text()
anchor = '    require(eglChooseConfig(display, attributes, &config, 1, &count) && count == 1, "choose config");'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    EGLConfig available[128];
    EGLint available_count = -1;
    EGLBoolean enumerated = eglGetConfigs(display, available, 128, &available_count);
    printf("FRONTEND931_CONFIGS ok=%u count=%d error=0x%x\n", enumerated, available_count, eglGetError());
    if (enumerated) for (EGLint i = 0; i < available_count && i < 128; ++i) {
        EGLint surface = -1, renderable = -1, red = -1, green = -1, blue = -1, alpha = -1;
        EGLBoolean ok = eglGetConfigAttrib(display, available[i], EGL_SURFACE_TYPE, &surface);
        ok &= eglGetConfigAttrib(display, available[i], EGL_RENDERABLE_TYPE, &renderable);
        ok &= eglGetConfigAttrib(display, available[i], EGL_RED_SIZE, &red);
        ok &= eglGetConfigAttrib(display, available[i], EGL_GREEN_SIZE, &green);
        ok &= eglGetConfigAttrib(display, available[i], EGL_BLUE_SIZE, &blue);
        ok &= eglGetConfigAttrib(display, available[i], EGL_ALPHA_SIZE, &alpha);
        printf("FRONTEND931_CONFIG index=%d ok=%u surface=0x%x renderable=0x%x rgba=%d,%d,%d,%d error=0x%x\n",
               i, ok, surface, renderable, red, green, blue, alpha, eglGetError());
    }
    count = -1;
    EGLBoolean chosen = eglChooseConfig(display, attributes, &config, 1, &count);
    printf("FRONTEND931_CHOOSE ok=%u count=%d error=0x%x\n", chosen, count, eglGetError());
    require(chosen && count == 1, "choose config");''')
source = source.replace('FRONTEND930_', 'FRONTEND931_')
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(libs / 'libEGL.so'), str(libs / 'libGLESv3.so'),
                '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
original = base / 'official-frontend-probe-930/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '21d82298b2f9e813ac9090a71a27efdc1052d54d1fa5684a890d987eb1658f72'
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

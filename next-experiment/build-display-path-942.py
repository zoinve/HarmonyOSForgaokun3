"""Compare official EGL display entry points without modifying its libraries."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-display-path-942'
work = root / 'display-path-942'
assert not out.exists() and not work.exists()
work.mkdir()
source = r'''
#define _GNU_SOURCE
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <dlfcn.h>
#include <stdio.h>
int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    const char *client = eglQueryString(EGL_NO_DISPLAY, EGL_EXTENSIONS);
    printf("DISPLAY942_CLIENT %s\n", client ? client : "NULL");
    PFNEGLGETPLATFORMDISPLAYEXTPROC get = (PFNEGLGETPLATFORMDISPLAYEXTPROC)
        eglGetProcAddress("eglGetPlatformDisplayEXT");
    Dl_info info = {0};
    if (get) dladdr((void *)get, &info);
    printf("DISPLAY942_FUNCTION pointer=%p file=%s symbol=%s\n", (void *)get,
        info.dli_fname ? info.dli_fname : "NULL", info.dli_sname ? info.dli_sname : "NULL");
    EGLDisplay ext = get ? get(0x34e0, NULL, NULL) : EGL_NO_DISPLAY;
    EGLint a = 0, b = 0;
    EGLBoolean ok = eglInitialize(ext, &a, &b);
    printf("DISPLAY942_EXT display=%p ok=%d version=%d.%d error=0x%x\n",
        (void *)ext, ok, a, b, eglGetError());
    EGLDisplay ordinary = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    a = b = 0;
    EGLBoolean direct = eglInitialize(ordinary, &a, &b);
    printf("DISPLAY942_DEFAULT display=%p ok=%d version=%d.%d error=0x%x equal=%d\n",
        (void *)ordinary, direct, a, b, eglGetError(), ext == ordinary);
    if (direct) eglTerminate(ordinary);
    puts("DISPLAY942_DONE desktop_not_tested=1");
    return direct ? 0 : 1;
}
'''
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(libs / 'libEGL.so'), '-ldl',
                '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
original = base / 'official-native-gbm-940/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '78226918d24c526971b9793755dac6e44bdda1eb79f8448d547d6f55ad056067'
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

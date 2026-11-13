"""Real SDK window draw/swap/consumer acquisition; no system-image changes."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-present-934'
work = root / 'native-present-934'
assert not out.exists() and not work.exists()
old = (base / 'official-native-window-933/initramfs.cpio.gz').read_bytes()
assert hashlib.sha256(old).hexdigest() == 'e173632f0430143cb2b381d858746f7721825f1472716a423ec3165b986f6a4f'
source = (root / 'native-window-933/probe.c').read_text()
anchor = '    require(eglDestroySurface(display, window_surface), "destroy real EGL window surface");'
assert source.count(anchor) == 1
source = '#include <poll.h>\n#include <unistd.h>\n' + source
source = source.replace(anchor, r'''
    int32_t (*acquire_buffer)(void *, void **, int *) = dlsym(native, "OH_NativeImage_AcquireNativeWindowBuffer");
    int32_t (*release_buffer)(void *, void *, int) = dlsym(native, "OH_NativeImage_ReleaseNativeWindowBuffer");
    require(acquire_buffer && release_buffer, "consumer buffer exports");
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    require(eglMakeCurrent(display, window_surface, window_surface, context), "make real window current");
    glViewport(0, 0, 16, 16);
    glClearColor(17.0f/255, 51.0f/255, 85.0f/255, 1);
    glClear(GL_COLOR_BUFFER_BIT);
    glFinish();
    unsigned char window_pixel[4] = {0};
    glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, window_pixel);
    require(glGetError() == GL_NO_ERROR, "read real window GPU pixel");
    printf("NATIVE934_WINDOW_PIXEL rgba=%u,%u,%u,%u\n", window_pixel[0], window_pixel[1], window_pixel[2], window_pixel[3]);
    require(window_pixel[0] == 17 && window_pixel[1] == 51 && window_pixel[2] == 85 && window_pixel[3] == 255, "real window GPU pixel");
    require(eglSwapBuffers(display, window_surface), "swap real window buffer");
    void *consumer_buffer = NULL;
    int fence = -1;
    int acquired = acquire_buffer(image, &consumer_buffer, &fence);
    printf("NATIVE934_CONSUMER status=%d buffer=%p fence=%d\n", acquired, consumer_buffer, fence);
    require(acquired == 0 && consumer_buffer != NULL, "acquire actual presented consumer buffer");
    if (fence >= 0) {
        struct pollfd wait_fence = {.fd=fence, .events=POLLIN};
        require(poll(&wait_fence, 1, 5000) == 1 && !(wait_fence.revents & (POLLERR|POLLNVAL)), "wait presented fence");
        close(fence);
    }
    require(release_buffer(image, consumer_buffer, -1) == 0, "release actual consumer buffer");
    require(eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, context), "restore surfaceless context");
    puts("NATIVE934_PRESENT_PASS real_window_gpu_pixel_swap_consumer_acquire_release desktop_not_tested=1");
''' + anchor)
source = source.replace('NATIVE933_', 'NATIVE934_')
source = source.replace('buffers_not_tested=1', 'consumer_cpu_pixels_not_tested=1')
work.mkdir()
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
    '-I' + str(root / 'prefix/include'), str(work / 'probe.c'), str(libs / 'libEGL.so'),
    str(libs / 'libGLESv3.so'), '-ldl', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
    '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
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
    if name == 'TRAILER!!!':
        break
assert changed == ['gpu-userspace-probe']
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    changed_entries=changed, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

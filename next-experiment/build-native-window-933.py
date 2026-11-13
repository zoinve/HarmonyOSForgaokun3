"""Real SDK consumer/window ownership fixture, diskless and separate from desktop."""
from pathlib import Path
import gzip
import hashlib
import json
import posixpath
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-window-933'
work = root / 'native-window-933'
assert not out.exists() and not work.exists()
work.mkdir()
original = base / 'official-frontend-probe-932/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == 'd79239a850d07326d787347471e490c217b2c7687fddcdca533b8372acf8899c'
raw = gzip.decompress(original.read_bytes())
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

private = 'system/lib64/lab-softpipe-167/'
image = '/mnt/d/Download/pc_all_arm/system.img'
queue, seen, added = ['libnative_image.so'], set(), []
folders = ['/system/lib64', '/system/lib64/chipset-sdk-sp', '/system/lib64/platformsdk',
           '/system/lib64/chipset-pub-sdk', '/system/lib64/chipset-sdk', '/system/lib64/ndk']
while queue:
    name = queue.pop()
    if name in seen or name == 'libc.so':
        continue
    seen.add(name)
    if private + name in entries:
        continue  # Existing official closure was preserved and tested in 932.
    for folder in folders:
        candidate = folder + '/' + name
        for _ in range(12):
            stat = subprocess.run(['debugfs', '-R', 'stat ' + candidate, image],
                                  capture_output=True, text=True, check=True).stdout
            link = re.search(r'Fast link dest: "(.*?)"', stat)
            if not link:
                break
            candidate = posixpath.normpath(posixpath.join(posixpath.dirname(candidate), link[1]))
        if 'Type: regular' in stat:
            break
    else:
        raise AssertionError(('missing official dependency', name))
    dest = work / name
    subprocess.run(['debugfs', '-R', f'dump {candidate} {dest}', image], capture_output=True, check=True)
    body = dest.read_bytes()
    assert body.startswith(b'\x7fELF')
    entries[private + name] = 0o100444, body
    queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]', subprocess.check_output(['readelf', '-dW', str(dest)], text=True)))
    added.append(dict(name=name, source=candidate, sha256=hashlib.sha256(body).hexdigest()))

source = (root / 'frontend-surfaceless-932/probe.c').read_text()
source = '#include <dlfcn.h>\n' + source
anchor = '    glDeleteFramebuffers(1, &framebuffer);'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    void *native = dlopen("libnative_image.so", RTLD_NOW | RTLD_LOCAL);
    if (!native) fprintf(stderr, "NATIVE933_DLOPEN %s\n", dlerror());
    require(native != NULL, "load official native image");
    void *(*create_consumer)(void) = dlsym(native, "OH_ConsumerSurface_Create");
    int32_t (*set_size)(void *, int32_t, int32_t) = dlsym(native, "OH_ConsumerSurface_SetDefaultSize");
    void *(*acquire_window)(void *) = dlsym(native, "OH_NativeImage_AcquireNativeWindow");
    int32_t (*get_id)(void *, uint64_t *) = dlsym(native, "OH_NativeImage_GetSurfaceId");
    void (*destroy_image)(void **) = dlsym(native, "OH_NativeImage_Destroy");
    require(create_consumer && set_size && acquire_window && get_id && destroy_image, "native image exports");
    void *image = create_consumer();
    require(image != NULL, "create real consumer");
    require(set_size(image, 16, 16) == 0, "set real consumer size");
    uint64_t surface_id = 0;
    require(get_id(image, &surface_id) == 0 && surface_id != 0, "real surface id");
    void *window = acquire_window(image);
    require(window != NULL, "acquire real native window");
    printf("NATIVE933_WINDOW id=%llu pointer=%p\n", (unsigned long long)surface_id, window);
    EGLSurface window_surface = eglCreateWindowSurface(display, config, (EGLNativeWindowType)window, NULL);
    require(window_surface != EGL_NO_SURFACE, "official EGL real window ownership");
    require(eglDestroySurface(display, window_surface), "destroy real EGL window surface");
    destroy_image(&image);
    require(image == NULL, "destroy native image");
    puts("NATIVE933_PASS real_consumer_window_and_egl_surface buffers_not_tested=1 desktop_not_tested=1");
''' + anchor)
source = source.replace('FRONTEND932_', 'NATIVE933_')
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(libs / 'libEGL.so'), str(libs / 'libGLESv3.so'), '-ldl',
                '-Wl,-rpath,/system/lib64/lab-softpipe-167', '-Wl,-rpath-link,' + str(libs),
                '-o', str(work / 'probe')], check=True)
entries['gpu-userspace-probe'] = 0o100755, (work / 'probe').read_bytes()

def entry(name, mode, body, inode):
    nb = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(nb), 0]
    head = b'070701' + b''.join(f'{v:08x}'.encode() for v in values) + nb
    return head + b'\0' * (-len(head) % 4) + body + b'\0' * (-len(body) % 4)

archive = gzip.compress(b''.join(entry(n, m, b, i) for i, (n, (m, b)) in
                                enumerate(sorted(entries.items()), 1)) +
                        entry('TRAILER!!!', 0, b'', len(entries) + 1), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    added_official_libraries=added, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

"""Restrict our bridge's unsupported client dispatch; exercise the RS selection path."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-display-capability-943'
work = root / 'display-capability-943'
assert not out.exists() and not work.exists()
work.mkdir()
source = (root / 'gbm-copy-912/bridge.cpp').read_text()
anchor = '        std::string extensions(base);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        // The SDK frontend exposes driver extension pointers without wrapping their
        // display handles. Only advertise client dispatch that works end-to-end.
        if (egl == EGL_NO_DISPLAY) {
            std::string compatible;
            size_t begin = 0;
            while (begin < extensions.size()) {
                size_t end = extensions.find(' ', begin);
                if (end == std::string::npos) end = extensions.size();
                std::string token = extensions.substr(begin, end - begin);
                if (!token.empty() && token != "EGL_EXT_platform_base" &&
                    token != "EGL_KHR_platform_base") {
                    if (!compatible.empty()) compatible += ' ';
                    compatible += token;
                }
                begin = end + 1;
            }
            extensions = std::move(compatible);
        }
''')
(work / 'bridge.cpp').write_text(source)
previous = root / 'window-bridge'
prefix = root / 'prefix/system'
libs = prefix / 'lib64/lab-virgl883'
cc = previous / 'toolchain/ohos-platform-cxx'
subprocess.run([str(cc), '-shared', '-fPIC', '-O2', '-std=c++17',
                '-DEGL_EGLEXT_PROTOTYPES', '-I' + str(previous),
                '-I' + str(previous / 'include'), '-I' + str(prefix / 'include'),
                '-I' + str(prefix / 'include/libdrm'), str(work / 'bridge.cpp'),
                str(previous / 'drm_device.o'), '-L' + str(libs),
                '-lGLESv2', '-lgbm', '-ldrm', '-ldl',
                '-Wl,--no-undefined,-soname,libEGL_impl.so', '-Wl,-Bsymbolic-functions',
                '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-o', str(work / 'libEGL_impl.so')], check=True)
probe = (root / 'native-alloc-handle-939/probe.c').read_text()
anchor = 'EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);'
assert probe.count(anchor) == 1
probe = probe.replace(anchor, '''const char *client943 = eglQueryString(EGL_NO_DISPLAY, EGL_EXTENSIONS);
    printf("DISPLAY943_CLIENT %s\\n", client943 ? client943 : "NULL");
    require(client943 && !strstr(client943, "EGL_EXT_platform_base") &&
            !strstr(client943, "EGL_KHR_platform_base"), "client dispatch capability");
    // Same advertised-capability decision used by the original RenderContextGL.
    EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    puts("DISPLAY943_RS_DEFAULT_SELECTED");''')
(work / 'probe.c').write_text(probe)
official = root / 'official-frontend-probe-927'
subprocess.run([str(previous / 'toolchain/ohos-cc'), '-O2',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(official / 'libEGL.so'), str(official / 'libGLESv3.so'), '-ldl',
                '-Wl,--export-dynamic', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(official), '-o', str(work / 'probe')], check=True)
original = base / 'official-native-gbm-940/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '78226918d24c526971b9793755dac6e44bdda1eb79f8448d547d6f55ad056067'
raw = gzip.decompress(original.read_bytes())
targets = {'gpu-userspace-probe': (work / 'probe').read_bytes(),
           'system/lib64/lab-softpipe-167/libEGL_impl.so': (work / 'libEGL_impl.so').read_bytes()}
chunks, changed, pos = [], [], 0
while True:
    start = pos
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + ns].decode()
    data = (pos + 110 + ns + 3) & ~3
    pos = (data + size + 3) & ~3
    if name in targets:
        body = targets[name]
        chunk = h[:54] + f'{len(body):08x}'.encode() + h[62:] + raw[start + 110:data] + body
        chunks.append(chunk + b'\0' * (-len(chunk) % 4))
        changed.append(name)
    else:
        chunks.append(raw[start:pos])
    if name == 'TRAILER!!!':
        break
assert set(changed) == set(targets)
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(
    initrd_sha256=hashlib.sha256(archive).hexdigest(), changed_entries=changed,
    bridge_sha256=hashlib.sha256(targets['system/lib64/lab-softpipe-167/libEGL_impl.so']).hexdigest(),
    official_libraries_unchanged=True, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

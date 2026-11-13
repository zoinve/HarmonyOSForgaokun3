"""Diagnostic copy: bounded EGL logging and the actual RS config request.

Only our bridge and diskless fixture change. Official DSOs remain untouched.
Run under WSL Debian Python; never resume a completed numbered archive.
"""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-egl-boundary-945'
work = root / 'egl-boundary-945'
assert not out.exists() and not work.exists()
parent = base / 'official-display-capability-943/initramfs.cpio.gz'
assert hashlib.sha256(parent.read_bytes()).hexdigest() == '1fcb2dd4be736dd1401218efcea7d900c6dc416c208076ecbbdc10edd394b8b0'
work.mkdir()
source = (root / 'display-capability-943/bridge.cpp').read_text()
start = source.index('static void gpu892_trace(const char *format, ...) {')
end = source.index('\n}\n', start) + 3
source = source[:start] + r'''static void gpu892_trace(const char *format, ...) {
 static unsigned count=0;
 if(__atomic_fetch_add(&count,1,__ATOMIC_RELAXED)>=256) return;
 int saved_errno=errno;
 char message[1536];
 va_list args;va_start(args,format);
 vsnprintf(message,sizeof(message),format,args);va_end(args);
 fprintf(stderr,"EGL945 pid=%ld %s",(long)getpid(),message);
 // Use the normal SDK log transport. Missing/denied logging is not bypassed.
 using Print = int (*)(int,int,unsigned,const char *,const char *,...);
 static Print print=reinterpret_cast<Print>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
 if(print) print(3,6,0xD001400,"EGL945","%{public}s",message);
 errno=saved_errno;
}
''' + source[end:]
anchor = '    if (!fn(egl, backing(draw), backing(read), context)) return EGL_FALSE;'
assert source.count(anchor) == 1
source = source.replace(anchor, '''    EGLBoolean made = fn(egl, backing(draw), backing(read), context);
    gpu892_trace("GPU945_MAKE_CURRENT display=%p draw=%p read=%p context=%p result=%u\\n",
                 egl, backing(draw), backing(read), context, made);
    if (!made) return EGL_FALSE;''')
(work / 'bridge.cpp').write_text(source)
previous = root / 'window-bridge'
prefix = root / 'prefix/system'
libs = prefix / 'lib64/lab-virgl883'
subprocess.run([str(previous / 'toolchain/ohos-platform-cxx'), '-shared', '-fPIC', '-O2', '-std=c++17',
                '-DEGL_EGLEXT_PROTOTYPES', '-I' + str(previous), '-I' + str(previous / 'include'),
                '-I' + str(prefix / 'include'), '-I' + str(prefix / 'include/libdrm'),
                str(work / 'bridge.cpp'), str(previous / 'drm_device.o'), '-L' + str(libs),
                '-lGLESv2', '-lgbm', '-ldrm', '-ldl', '-Wl,--no-undefined,-soname,libEGL_impl.so',
                '-Wl,-Bsymbolic-functions', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-o', str(work / 'libEGL_impl.so')], check=True)
probe = (root / 'display-capability-943/probe.c').read_text()
assert probe.count('EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT') == 1
# Actual RS .rodata at 0x34a7bc requests WINDOW/RGBA8/ES3_BIT and a version-2 context.
probe = probe.replace('EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT', 'EGL_RENDERABLE_TYPE, 0x0040')
probe = probe.replace('puts("DISPLAY943_RS_DEFAULT_SELECTED");', 'puts("EGL945_RS_CONFIG_REQUEST");')
(work / 'probe.c').write_text(probe)
official = root / 'official-frontend-probe-927'
subprocess.run([str(previous / 'toolchain/ohos-cc'), '-O2', '-I' + str(root / 'prefix/include'),
                str(work / 'probe.c'), str(official / 'libEGL.so'), str(official / 'libGLESv3.so'),
                '-ldl', '-Wl,--export-dynamic', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(official), '-o', str(work / 'probe')], check=True)
targets = {'gpu-userspace-probe': (work / 'probe').read_bytes(),
           'system/lib64/lab-softpipe-167/libEGL_impl.so': (work / 'libEGL_impl.so').read_bytes()}
raw = gzip.decompress(parent.read_bytes())
pos, chunks, changed = 0, [], []
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

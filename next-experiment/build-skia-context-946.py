"""Diskless public Drawing GPU-context diagnostic; original SDK DSOs unchanged."""
from pathlib import Path
import gzip
import hashlib
import json
import posixpath
import re
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out, work = base / 'official-skia-context-946', root / 'skia-context-946'
assert not out.exists() and not work.exists()
parent = base / 'official-egl-boundary-945/initramfs.cpio.gz'
assert hashlib.sha256(parent.read_bytes()).hexdigest() == '58ed43d5b7ab42fd24a26fda4d72a53c748d28f22c926bd199f91d5bda6ce281'
work.mkdir()
raw = gzip.decompress(parent.read_bytes())
entries, pos = {}, 0
while True:
    h = raw[pos:pos + 110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos + 110:pos + 109 + ns].decode()
    data = (pos + 110 + ns + 3) & ~3
    pos = (data + size + 3) & ~3
    if name == 'TRAILER!!!':
        break
    assert name not in entries
    entries[name] = int(h[14:22], 16), raw[data:data + size]

private = 'system/lib64/lab-softpipe-167/'
queue, seen, added = ['libnative_drawing_ndk.z.so'], set(), []
image = '/mnt/d/Download/pc_all_arm/system.img'
folders = ['/system/lib64', '/system/lib64/chipset-sdk-sp', '/system/lib64/platformsdk',
           '/system/lib64/chipset-pub-sdk', '/system/lib64/chipset-sdk', '/system/lib64/ndk']
while queue:
    name = queue.pop()
    if name in seen or name == 'libc.so':
        continue
    seen.add(name)
    if private + name in entries:
        continue  # Existing, unchanged closure was exercised in 945.
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
        raise AssertionError(('missing original SDK dependency', name))
    dest = work / name
    subprocess.run(['debugfs', '-R', f'dump {candidate} {dest}', image], capture_output=True, check=True)
    body = dest.read_bytes()
    assert body.startswith(b'\x7fELF')
    entries[private + name] = 0o100444, body
    queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]', subprocess.check_output(['readelf', '-dW', str(dest)], text=True)))
    added.append(dict(name=name, source=candidate, sha256=hashlib.sha256(body).hexdigest()))

source = (root / 'egl-boundary-945/probe.c').read_text()
source = '#include <stdbool.h>\n' + source
anchor = '    GLuint framebuffer, color;'
# Insert directly after the first successful make-current, before any shader/FBO test.
lines = source.splitlines(keepends=True)
indices = [i for i, line in enumerate(lines) if '"surfaceless make current"' in line or '"surfaceless current"' in line]
if not indices:
    indices = [i for i, line in enumerate(lines) if 'require(eglMakeCurrent(display, EGL_NO_SURFACE' in line]
assert len(indices) == 1
insertion = r'''
    puts("SKIA946_BEGIN public_CreateFromGL");
    void *drawing = dlopen("libnative_drawing_ndk.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!drawing) fprintf(stderr, "SKIA946_DLOPEN %s\n", dlerror());
    require(drawing != NULL, "load original Drawing library");
    typedef struct { bool allowPathMaskCaching; } DrawingOptions;
    void *(*create_gpu)(DrawingOptions) = dlsym(drawing, "OH_Drawing_GpuContextCreateFromGL");
    void (*destroy_gpu)(void *) = dlsym(drawing, "OH_Drawing_GpuContextDestroy");
    require(create_gpu && destroy_gpu, "original Drawing exports");
    DrawingOptions options = {true};
    puts("SKIA946_CALL CreateFromGL");
    void *gpu = create_gpu(options);
    printf("SKIA946_RESULT context=%p\n", gpu);
    require(gpu != NULL, "original Skia GPU context");
    destroy_gpu(gpu);
    puts("SKIA946_CONTEXT_PASS original_Drawing_BuildFromGL desktop_not_tested=1");
'''
lines.insert(indices[0] + 1, insertion)
source = ''.join(lines)
(work / 'probe.c').write_text(source)
cc = str(root / 'window-bridge/toolchain/ohos-cc')
official = root / 'official-frontend-probe-927'
subprocess.run([cc, '-O2', '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(official / 'libEGL.so'), str(official / 'libGLESv3.so'), '-ldl',
                '-Wl,--export-dynamic', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(official), '-o', str(work / 'probe')], check=True)
fault = (base / 'frontend-fault-928.c').read_text()
fault = fault.replace('    sigaction(SIGBUS, &action, NULL);',
                      '    sigaction(SIGILL, &action, NULL);\n    sigaction(SIGBUS, &action, NULL);')
(work / 'fault.c').write_text(fault)
subprocess.run([cc, '-shared', '-fPIC', '-O2', str(work / 'fault.c'), '-o', str(work / 'fault.so')], check=True)
assert 'frontend-fault.so' in entries
entries['gpu-userspace-probe'] = 0o100755, (work / 'probe').read_bytes()
entries['frontend-fault.so'] = entries['frontend-fault.so'][0], (work / 'fault.so').read_bytes()

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
    added_official_libraries=added, changed_existing_entries=['gpu-userspace-probe', 'frontend-fault.so'],
    disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())

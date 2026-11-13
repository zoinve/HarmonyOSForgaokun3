"""Exercise supported GBM configs with surfaceless context and real texture FBO."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-frontend-probe-932'
work = root / 'frontend-surfaceless-932'
assert not out.exists() and not work.exists()
work.mkdir()
source = (root / 'frontend-default-930/probe.c').read_text()
source = source.replace('EGL_SURFACE_TYPE, EGL_PBUFFER_BIT', 'EGL_SURFACE_TYPE, EGL_WINDOW_BIT')
start = source.index('    EGLint surface_attributes[]')
end = source.index('    const char *renderer', start)
source = source[:start] + r'''
    const char *extensions = eglQueryString(display, EGL_EXTENSIONS);
    printf("FRONTEND932_EXTENSIONS %s\n", extensions ? extensions : "NULL");
    require(extensions && strstr(extensions, "EGL_KHR_surfaceless_context"), "surfaceless supported");
    require(eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, context), "surfaceless make current");
    GLuint texture = 0, framebuffer = 0;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 16, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "texture framebuffer complete");
''' + source[end:]
source = source.replace('    eglDestroySurface(display, surface);', '')
source = source.replace('    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);',
                        '    glDeleteFramebuffers(1, &framebuffer);\n    glDeleteTextures(1, &texture);\n    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);')
source = source.replace('FRONTEND930_', 'FRONTEND932_')
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
                '-I' + str(root / 'prefix/include'), str(work / 'probe.c'),
                str(libs / 'libEGL.so'), str(libs / 'libGLESv3.so'),
                '-Wl,-rpath,/system/lib64/lab-softpipe-167',
                '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
original = base / 'official-frontend-probe-931/initramfs.cpio.gz'
assert hashlib.sha256(original.read_bytes()).hexdigest() == '09012cb245f4961463119e8a50380350d9edb5066cc572a87e7a16f25fddfc21'
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

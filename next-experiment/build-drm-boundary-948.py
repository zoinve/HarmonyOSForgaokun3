"""Diagnostic-only copy of our DRM selector; no access-policy changes.

Run under WSL. Completed numbered artifacts are never reused or overwritten.
"""
from pathlib import Path
import subprocess
import sys

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'drm-boundary-948'
assert not (base / 'official-drm-boundary-948').exists()
if sys.argv[1:] == ['--resume-incomplete']:
    assert work.is_dir()
else:
    assert not work.exists()
    work.mkdir()
source = (root / 'window-bridge/drm_device.c').read_text()
source = source.replace('#include <stdio.h>', '''#include <stdio.h>
#include <sys/stat.h>
extern void AuroraDrmTrace948(const char *, ...);
#define TRACE(...) do { int saved = errno; AuroraDrmTrace948(__VA_ARGS__); errno = saved; } while (0)''')
changes = {
    '    AuroraDrmDisplay best = {.fd = -1};':
        '    TRACE("DRM948_BEGIN uid=%u gid=%u own=%d\\n", (unsigned)geteuid(), (unsigned)getegid(), own_display);\n    AuroraDrmDisplay best = {.fd = -1};',
    '        if (fd < 0) continue;': '''        if (fd < 0) {
            int error = errno; struct stat st; int status = stat(path, &st);
            TRACE("DRM948_OPEN path=%s fd=-1 errno=%d stat=%d mode=%o uid=%u gid=%u\\n", path, error, status,
                  status ? 0 : st.st_mode, status ? 0 : st.st_uid, status ? 0 : st.st_gid);
            continue;
        }
        TRACE("DRM948_OPEN path=%s fd=%d\\n", path, fd);''',
    '        drmModeRes *resources = drmModeGetResources(fd);': '''        TRACE("DRM948_VERSION fd=%d name=%s\\n", fd, version->name);
        drmModeRes *resources = drmModeGetResources(fd);
        TRACE("DRM948_RESOURCES fd=%d ok=%d errno=%d connectors=%d crtcs=%d\\n", fd, resources != NULL, errno,
              resources ? resources->count_connectors : -1, resources ? resources->count_crtcs : -1);''',
    '            if (!connector) continue;': '''            if (!connector) { TRACE("DRM948_CONNECTOR id=%u null errno=%d\\n", resources->connectors[n], errno); continue; }
            TRACE("DRM948_CONNECTOR id=%u connection=%d modes=%d encoders=%d\\n", connector->connector_id,
                  connector->connection, connector->count_modes, connector->count_encoders);''',
    '                if (!encoder) continue;': '''                if (!encoder) { TRACE("DRM948_ENCODER null errno=%d\\n", errno); continue; }
                TRACE("DRM948_ENCODER id=%u possible=%x crtc=%u\\n", encoder->encoder_id, encoder->possible_crtcs, encoder->crtc_id);''',
    '            best.fd = dup(fd);': '            best.fd = dup(fd);\n            TRACE("DRM948_DUP source=%d result=%d errno=%d\\n", fd, best.fd, errno);',
    '    *display = best;': '    TRACE("DRM948_SELECTED fd=%d driver=%s connector=%u crtc=%u\\n", best.fd, best.driver, best.connector, best.crtc);\n    *display = best;',
    '            if (version) drmFreeVersion(version);': '            TRACE("DRM948_VERSION_REJECT fd=%d version=%p errno=%d\\n", fd, (void *)version, errno);\n            if (version) drmFreeVersion(version);',
}
for old, new in changes.items():
    assert source.count(old) == 1, old
    source = source.replace(old, new)
(work / 'drm_device.c').write_text(source)
previous = root / 'window-bridge'
prefix = root / 'prefix/system'
subprocess.run([str(previous / 'toolchain/ohos-cc'), '-fPIC', '-O2',
                '-I' + str(previous), '-I' + str(prefix / 'include'),
                '-I' + str(prefix / 'include/libdrm'), '-c', str(work / 'drm_device.c'),
                '-o', str(work / 'drm_device.o')], check=True)
builder = (base / 'build-egl-boundary-945.py').read_text()
builder = builder.replace("out = base / 'official-egl-boundary-945'", "out = base / 'official-drm-boundary-948'")
builder = builder.replace("work = root / 'egl-boundary-945'", "work = root / 'drm-boundary-948'")
builder = builder.replace('assert not out.exists() and not work.exists()', 'assert not out.exists() and work.is_dir()')
builder = builder.replace('work.mkdir()', '# Own work directory was created above.')
anchor = "(work / 'bridge.cpp').write_text(source)"
assert builder.count(anchor) == 1
callback = '''
extern "C" void AuroraDrmTrace948(const char *format, ...) {
 int saved=errno; char message[1536]; va_list args; va_start(args,format);
 vsnprintf(message,sizeof(message),format,args); va_end(args);
 gpu892_trace("%s",message); errno=saved;
}
'''
builder = builder.replace(anchor, 'source += ' + repr(callback) + '\n' + anchor)
assert builder.count("str(previous / 'drm_device.o')") == 1
builder = builder.replace("str(previous / 'drm_device.o')", "str(work / 'drm_device.o')")
exec(compile(builder, 'derived-drm-boundary-948', 'exec'))

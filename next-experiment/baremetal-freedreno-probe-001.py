"""Derive a render-node-only OHOS probe, retaining the earlier triangle test."""
from pathlib import Path


def build_source():
    parent = Path(__file__).with_name('gpu-userspace-probe.c').read_text()
    parent = parent.replace('/* Throwaway, diskless OHOS EGL/GLES smoke test; not desktop evidence. */',
                            '/* OHOS Freedreno offscreen-only test; no modeset or desktop claim. */')
    parent = parent.replace('#include <string.h>', '#include <string.h>\n#include "baremetal-freedreno-policy-001.h"')
    parent = parent.replace('GPU883_', 'FREEDRENO001_')
    old = '    EGLDisplay display = platform(EGL_PLATFORM_DEVICE_EXT, devices[0], NULL);'
    new = '''    PFNEGLQUERYDEVICESTRINGEXTPROC device_string =
        (PFNEGLQUERYDEVICESTRINGEXTPROC)eglGetProcAddress("eglQueryDeviceStringEXT");
    require(device_string != NULL, "query device render node");
    EGLDeviceEXT selected = EGL_NO_DEVICE_EXT;
    for (EGLint i = 0; i < count && i < 8; ++i) {
        const char *node = device_string(devices[i], EGL_DRM_RENDER_NODE_FILE_EXT);
        printf("FREEDRENO001_DEVICE index=%d render_node=%s\\n", i, node ? node : "NULL");
        if (node && !strcmp(node, "/dev/dri/renderD128")) selected = devices[i];
    }
    require(selected != EGL_NO_DEVICE_EXT, "select explicit renderD128");
    EGLDisplay display = platform(EGL_PLATFORM_DEVICE_EXT, selected, NULL);'''
    assert parent.count(old) == 1
    parent = parent.replace(old, new)
    old = 'renderer && strstr(renderer, "virgl") && !strstr(renderer, "llvmpipe") && !strstr(renderer, "softpipe"), "hardware VirGL renderer"'
    assert parent.count(old) == 1
    parent = parent.replace(old, 'freedreno_renderer_ok(renderer), "native FD690 renderer"')
    old = 'center[0] > 240 && center[1] < 16 && center[2] < 16 && corner[0] < 16 && corner[2] > 240'
    assert parent.count(old) == 1
    parent = parent.replace(old, 'freedreno_pixels_ok(center, corner)')
    return parent

"""Exercise real sync_file export/poll/import instead of relying on glFinish."""
from pathlib import Path
import runpy


def build_source():
    base=Path(__file__).resolve().parent
    source=runpy.run_path(str(base/'baremetal-freedreno-dmabuf-probe-001.py'))['build_source']()
    source=source.replace('DMABUF001_','FENCE001_')
    source=source.replace('#include <unistd.h>','#include <unistd.h>\n#include <poll.h>')
    anchor='    glFinish();'
    assert source.count(anchor)==1
    source=source.replace(anchor,'''    require(strstr(extensions, "EGL_ANDROID_native_fence_sync") != NULL,
            "native fence extension");
    PFNEGLCREATESYNCKHRPROC create_sync = (PFNEGLCREATESYNCKHRPROC)eglGetProcAddress("eglCreateSyncKHR");
    PFNEGLDESTROYSYNCKHRPROC destroy_sync = (PFNEGLDESTROYSYNCKHRPROC)eglGetProcAddress("eglDestroySyncKHR");
    PFNEGLCLIENTWAITSYNCKHRPROC client_wait = (PFNEGLCLIENTWAITSYNCKHRPROC)eglGetProcAddress("eglClientWaitSyncKHR");
    PFNEGLGETSYNCATTRIBKHRPROC get_sync = (PFNEGLGETSYNCATTRIBKHRPROC)eglGetProcAddress("eglGetSyncAttribKHR");
    PFNEGLDUPNATIVEFENCEFDANDROIDPROC dup_fence =
        (PFNEGLDUPNATIVEFENCEFDANDROIDPROC)eglGetProcAddress("eglDupNativeFenceFDANDROID");
    require(create_sync && destroy_sync && client_wait && get_sync && dup_fence, "native fence entry points");
    const EGLint new_fence[] = {EGL_SYNC_NATIVE_FENCE_FD_ANDROID, EGL_NO_NATIVE_FENCE_FD_ANDROID, EGL_NONE};
    EGLSyncKHR sync = create_sync(display, EGL_SYNC_NATIVE_FENCE_ANDROID, new_fence);
    require(sync != EGL_NO_SYNC_KHR, "create GPU completion native fence");
    glFlush();
    int fence_fd = dup_fence(display, sync);
    require(fence_fd >= 0, "export sync_file fd");
    struct pollfd pending = {.fd=fence_fd, .events=POLLIN};
    int polled = poll(&pending, 1, 3000);
    printf("FENCE001_SYNC_FILE poll=%d revents=0x%x\\n", polled, pending.revents);
    require(polled == 1 && (pending.revents & POLLIN) &&
            !(pending.revents & (POLLERR | POLLHUP | POLLNVAL)), "native fence completion bounded poll");
    const EGLint imported_fence[] = {EGL_SYNC_NATIVE_FENCE_FD_ANDROID, fence_fd, EGL_NONE};
    EGLSyncKHR shared_sync = create_sync(display, EGL_SYNC_NATIVE_FENCE_ANDROID, imported_fence);
    require(shared_sync != EGL_NO_SYNC_KHR, "reimport sync_file fd with ownership transfer");
    EGLint waited = client_wait(display, shared_sync, 0, 1000000000ULL);
    EGLint signal_state = EGL_UNSIGNALED_KHR;
    require(waited == EGL_CONDITION_SATISFIED_KHR &&
            get_sync(display, shared_sync, EGL_SYNC_STATUS_KHR, &signal_state) &&
            signal_state == EGL_SIGNALED_KHR, "imported native fence signaled status");
    printf("FENCE001_REIMPORT wait=0x%x status=0x%x\\n", waited, signal_state);
    require(destroy_sync(display, shared_sync) && destroy_sync(display, sync), "native fence cleanup");
''')
    source=source.replace('PASS gbm_dmabuf_egl_and_second_device_readback desktop_not_tested=1',
                          'PASS native_fence_and_dmabuf_coherence desktop_not_tested=1')
    return source

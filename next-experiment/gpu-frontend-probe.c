/* Throwaway diagnostic: real OHOS EGL loading, no service impersonation. */
#include <dlfcn.h>
#include <stdio.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>

int main(int argc, char **argv)
{
    setbuf(stdout, NULL);
    const char *path = argc > 1 ? argv[1] : "/system/lib64/libEGL.so";
    void *lib = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    printf("GPU885_LOAD path=%s handle=%p error=%s\n", path, lib, lib ? "none" : dlerror());
    if (!lib) return 2;
    PFNEGLGETDISPLAYPROC get = (PFNEGLGETDISPLAYPROC)dlsym(lib, "eglGetDisplay");
    PFNEGLINITIALIZEPROC initialize = (PFNEGLINITIALIZEPROC)dlsym(lib, "eglInitialize");
    PFNEGLGETERRORPROC error = (PFNEGLGETERRORPROC)dlsym(lib, "eglGetError");
    PFNEGLQUERYSTRINGPROC query = (PFNEGLQUERYSTRINGPROC)dlsym(lib, "eglQueryString");
    if (!get || !initialize || !error || !query) return 3;
    EGLDisplay display = get(EGL_DEFAULT_DISPLAY);
    EGLint major = 0, minor = 0;
    EGLBoolean ok = initialize(display, &major, &minor);
    printf("GPU885_INITIALIZE path=%s display=%p ok=%u version=%d.%d error=%x\n",
           path, display, ok, major, minor, error());
    if (!ok) return 4;
    printf("GPU885_VENDOR %s\nGPU885_EXTENSIONS %s\n", query(display, EGL_VENDOR), query(display, EGL_EXTENSIONS));
    puts("GPU885_DISPLAY_ONLY desktop_not_tested=1");
    return 0;
}

"""Instrument our bridge only; do not consume EGL errors or change decisions."""
HEADER=r'''
static void trace025(const char *stage, long value, const void *pointer=nullptr)
{
    int saved=errno;
    static unsigned calls=0;
    if (__atomic_add_fetch(&calls,1,__ATOMIC_RELAXED)<=64) {
        using Print025=int (*)(int,int,unsigned,const char *,const char *,...);
        static auto print=reinterpret_cast<Print025>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
        if (print) print(3,4,0xD02510,"CommercialEGL025",
            "EGL025 stage=%{public}s value=%{public}ld pointer=%{public}p errno=%{public}d",
            stage,value,pointer,saved);
    }
    errno=saved;
}
'''

def instrument(source):
    assert 'trace025' not in source
    def replace(old,new):
        nonlocal source
        assert source.count(old)==1,old
        source=source.replace(old,new,1)
    replace('#include <vector>','#include <vector>\n'+HEADER)
    replace('    return library;','    trace025("mesa",library!=nullptr,library);\n    return library;')
    replace('EGLDisplay eglGetPlatformDisplayEXT(EGLenum platform, void *native, const EGLint *attributes)\n{',
            'EGLDisplay eglGetPlatformDisplayEXT(EGLenum platform, void *native, const EGLint *attributes)\n{\n    trace025("platform-entry",platform,native);')
    replace('    auto fn = real<PFNEGLGETPLATFORMDISPLAYEXTPROC>("eglGetPlatformDisplayEXT");',
            '    auto fn = real<PFNEGLGETPLATFORMDISPLAYEXTPROC>("eglGetPlatformDisplayEXT");\n    trace025("platform-symbol",fn!=nullptr);')
    replace('    if (AuroraOpenDisplayDrm(&display.drm, 0))',
            '    int drm_result025=AuroraOpenDisplayDrm(&display.drm, 0);\n    trace025("drm-open",drm_result025);\n    if (drm_result025)')
    replace('    display.device = gbm_create_device(display.drm.fd);',
            '    display.device = gbm_create_device(display.drm.fd);\n    trace025("gbm-device",display.drm.fd,display.device);')
    replace('    display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);',
            '    display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);\n    trace025("mesa-display",display.egl!=EGL_NO_DISPLAY,display.egl);')
    return source

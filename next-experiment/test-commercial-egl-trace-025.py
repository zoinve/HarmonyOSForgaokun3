"""Offline contract for bounded diagnostics, not target GPU success."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-egl-trace-025.py').exists(), 'missing bounded EGL boundary tracing'
instrument=runpy.run_path(str(base/'commercial-egl-trace-025.py'))['instrument']
fixture='''#include <vector>
void *mesa()
{
    static void *library = dlopen("/system/lib64/lab-commercial013/libEGL.so.1", RTLD_NOW | RTLD_LOCAL);
    return library;
}
EGLDisplay eglGetPlatformDisplayEXT(EGLenum platform, void *native, const EGLint *attributes)
{
    auto fn = real<PFNEGLGETPLATFORMDISPLAYEXTPROC>("eglGetPlatformDisplayEXT");
    if (AuroraOpenDisplayDrm(&display.drm, 0)) { error(EGL_NOT_INITIALIZED); return EGL_NO_DISPLAY; }
    display.device = gbm_create_device(display.drm.fd);
    display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);
    return display.egl;
}
'''
new=instrument(fixture)
for stage in ['mesa','platform-entry','platform-symbol','drm-open','gbm-device','mesa-display']:
    assert '"'+stage+'"' in new,stage
assert '<=64' in new and 'errno=saved' in new
assert 'HiLogPrint' in new and '%{public}' in new
assert 'eglGetError(' not in new, 'diagnostics must not consume the application error state'
assert 'O_CREAT' not in new and 'setuid' not in new and 'LD_PRELOAD' not in new
assert fixture.count('return EGL_NO_DISPLAY')==new.count('return EGL_NO_DISPLAY')
assert 'int drm_result025=AuroraOpenDisplayDrm(&display.drm, 0);' in new
with_error=False
try:instrument(new)
except AssertionError:with_error=True
assert with_error,'reject duplicate instrumentation'
header=runpy.run_path(str(base/'commercial-egl-trace-025.py'))['HEADER']
program='#include <cerrno>\n#include <dlfcn.h>\n'+header+r'''
static int count=0;
extern "C" int HiLogPrint(int type,int level,unsigned domain,const char *,const char *,...) {
 if(type!=3 || level!=4 || domain!=0xD02510) return -1;
 ++count;errno=99;return 0;
}
int main(){
 for(int i=0;i<80;++i){errno=17;trace025("test",i);if(errno!=17)return 1;}
 return count==64 ? 0 : 2;
}
'''
script='program='+repr(program)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='commercial-egl-trace025-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(program)
 subprocess.run(['c++','-rdynamic',str(p/'test.cpp'),'-ldl','-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True,timeout=60)
print('PASS: bounded public diagnostics; original failure returns and EGL error state preserved')

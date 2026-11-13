"""Fresh 892: persist bounded EGL call traces; no rendering behavior changes."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-892'
assert not out.exists()
out.mkdir()
script = r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'present-trace-892';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'gles-alias-probe-891/ramroot',ram,symlinks=True)
bridge=(root/'dispatch-probe-888/egl_window_bridge.cpp').read_text()
helper="""
#include <cstdarg>
static void gpu892_trace(const char *format, ...) {
 static unsigned count=0;
 if(__atomic_fetch_add(&count,1,__ATOMIC_RELAXED)>=200) return;
 char path[128];std::snprintf(path,sizeof(path),"/data/local/tmp/gpu892-%ld.log",(long)getpid());
 FILE *f=std::fopen(path,"a");if(!f)return;
 va_list args;va_start(args,format);std::vfprintf(f,format,args);va_end(args);
 std::fclose(f);
}
"""
anchor='extern "C" EGLDisplay eglGetDisplay(EGLNativeDisplayType native)'
assert bridge.count(anchor)==1
bridge=bridge.replace(anchor,helper+'\n'+anchor)
bridge=bridge.replace('std::fprintf(stderr,"GPU888_', 'gpu892_trace("GPU888_')
bridge=bridge.replace('std::fprintf(stderr,"%x:%x,",a[i],a[i+1]);','gpu892_trace("%x:%x,",a[i],a[i+1]);')
bridge=bridge.replace('std::fprintf(stderr,"\\n");','gpu892_trace("\\n");')
for signature in [
 'extern "C" EGLSurface eglCreateWindowSurface(EGLDisplay egl, EGLConfig config, EGLNativeWindowType native, const EGLint *attributes)',
 'extern "C" EGLBoolean eglMakeCurrent(EGLDisplay egl, EGLSurface draw, EGLSurface read, EGLContext context)',
 'extern "C" EGLBoolean eglSwapBuffers(EGLDisplay egl, EGLSurface surface)']:
 anchor=signature+'\n{';assert bridge.count(anchor)==1
 bridge=bridge.replace(anchor,anchor+'\n    gpu892_trace("GPU892_ENTER '+signature.split('(')[0].split()[-1]+'\\n");')
old='FORWARD(EGLBoolean, eglInitialize, (EGLDisplay d, EGLint *a, EGLint *b), (d,a,b), EGL_FALSE)'
assert bridge.count(old)==1
bridge=bridge.replace(old,'extern "C" EGLBoolean eglInitialize(EGLDisplay d,EGLint *a,EGLint *b) { auto fn=real<decltype(&eglInitialize)>("eglInitialize"); EGLBoolean r=fn?fn(d,a,b):EGL_FALSE; gpu892_trace("GPU892_INITIALIZE d=%p result=%u\\n",d,r);return r;}')
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17',
 '-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),
 '-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),
 str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl',
 '-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions',
 '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],
 stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-892')
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=script + archive, text=True, check=True)

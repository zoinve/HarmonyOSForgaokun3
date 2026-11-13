"""Fresh 888: diagnostic-only EGL call tracing and GL dispatch provenance."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-888'
assert not out.exists()
out.mkdir()
script = r"""
from pathlib import Path
import shutil,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'dispatch-probe-888';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
probe=(local/'gpu-context-probe.c').read_text()
probe='#define _GNU_SOURCE\n'+probe
anchor='    if (!renderer || !strstr(renderer, "virgl")) return 8;'
assert probe.count(anchor)==1
probe=probe.replace(anchor,r'''
    EGL_LOAD(eglGetCurrentContext); EGL_LOAD(eglQueryContext);
    EGLint client_version=0;
    EGLBoolean queried=p_eglQueryContext(display,context,EGL_CONTEXT_CLIENT_VERSION,&client_version);
    printf("GPU888_CONTEXT_STATE current=%p expected=%p queried=%u version=%d\n",
        p_eglGetCurrentContext(),context,queried,client_version);
    Dl_info info={0};
    if(dladdr((void*)p_glGetString,&info)) printf("GPU888_GL_PROC library=%s symbol=%s\n",
        info.dli_fname?info.dli_fname:"NULL",info.dli_sname?info.dli_sname:"NULL");
    void *gles=dlopen("/system/lib64/lab-softpipe-167/libGLESv2.so.2",RTLD_NOW|RTLD_LOCAL);
    const GLubyte *(*direct)(GLenum)=gles?dlsym(gles,"glGetString"):NULL;
    const char *native=direct?(const char*)direct(GL_RENDERER):NULL;
    printf("GPU888_DIRECT_GL renderer=%s\n",native?native:"NULL");
'''+anchor)
(work/'probe.c').write_text(probe)
prefix=root/'prefix/system'
subprocess.run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',
 '-I'+str(prefix/'include'),str(work/'probe.c'),'-ldl','-o',str(work/'gpu-frontend-probe')],check=True)
bridge=(root/'system-overlay-883/egl_window_bridge.cpp').read_text()
choose='FORWARD(EGLBoolean, eglChooseConfig, (EGLDisplay d, const EGLint *a, EGLConfig *c, EGLint s, EGLint *n), (d,a,c,s,n), EGL_FALSE)'
assert bridge.count(choose)==1
bridge=bridge.replace(choose,r'''
extern "C" EGLBoolean eglChooseConfig(EGLDisplay d,const EGLint *a,EGLConfig *c,EGLint s,EGLint *n)
{
 auto fn=real<decltype(&eglChooseConfig)>("eglChooseConfig");
 EGLBoolean result=fn?fn(d,a,c,s,n):EGL_FALSE;
 static unsigned count=0;
 if(__atomic_fetch_add(&count,1,__ATOMIC_RELAXED)<24) {
  std::fprintf(stderr,"GPU888_CHOOSE result=%u count=%d attrs=",result,n?*n:-1);
  if(a)for(unsigned i=0;i<64&&a[i]!=EGL_NONE;i+=2)std::fprintf(stderr,"%x:%x,",a[i],a[i+1]);
  std::fprintf(stderr,"\n");
 }
 return result;
}
''')
ctx='FORWARD(EGLContext, eglCreateContext, (EGLDisplay d, EGLConfig c, EGLContext s, const EGLint *a), (d,c,s,a), EGL_NO_CONTEXT)'
assert bridge.count(ctx)==1
bridge=bridge.replace(ctx,r'''
extern "C" EGLContext eglCreateContext(EGLDisplay d,EGLConfig c,EGLContext s,const EGLint *a)
{
 auto fn=real<decltype(&eglCreateContext)>("eglCreateContext");
 EGLContext result=fn?fn(d,c,s,a):EGL_NO_CONTEXT;
 std::fprintf(stderr,"GPU888_CREATE_CONTEXT result=%p\n",result);return result;
}
''')
(work/'egl_window_bridge.cpp').write_text(bridge)
previous=root/'window-bridge'
with (work/'bridge-build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17',
  '-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),
  '-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'egl_window_bridge.cpp'),
  str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl',
  '-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions',
  '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'libEGL_impl.so')],
  stdout=log,stderr=subprocess.STDOUT,check=True)
ram=work/'ramroot';shutil.copytree(root/'context-probe-887/ramroot',ram,symlinks=True)
shutil.copy2(work/'libEGL_impl.so',ram/'gpu883-libs/libEGL_impl.so')
shutil.copy2(work/'gpu-frontend-probe',ram/'gpu883-libs/gpu-frontend-probe')
"""
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True)
original=(base/'build-gpu-payload.py').read_text()
archive=original.split('def entry(',1)[1].split("'''",1)[0]
archive='def entry('+archive
setup="from pathlib import Path\nimport gzip,hashlib,json\nlocal=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-888')\nram=Path('/home/zoinve/harmony-virgl-883/dispatch-probe-888/ramroot')\n"
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=setup+archive,text=True,check=True)

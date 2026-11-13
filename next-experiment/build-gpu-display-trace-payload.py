"""Fresh 894: observe failed RS display/context inputs, without changing EGL behavior."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
out=base/'payload-894';assert not out.exists()
source=(base/'payload-893/init.c').read_text()
anchor='if(!strstr(name,"render_service"))continue;'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+r'''
        const char *nodes[]={"card0","renderD128"};
        for(unsigned ni=0;ni<2;ni++) {
          struct stat st;
          snprintf(path,sizeof(path),"/proc/%.32s/root/dev/dri/%s",gpu_entry->d_name,nodes[ni]);
          int rc=stat(path,&st);
          printf("GPU894_NODE path=%s rc=%d errno=%d mode=%o uid=%u gid=%u\n",path,rc,rc?errno:0,rc?0:(unsigned)st.st_mode,rc?0:st.st_uid,rc?0:st.st_gid);
        }
''')
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-894'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script=r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'display-trace-894';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'ram-trace-893/ramroot',ram,symlinks=True)
bridge=(root/'ram-trace-893/bridge.cpp').read_text()
anchor='extern "C" EGLint eglGetError()'
assert bridge.count(anchor)==1
bridge=bridge.replace(anchor,'static void gpu892_trace(const char *, ...);\n'+anchor)
for signature in [
 'extern "C" EGLDisplay eglGetPlatformDisplayEXT(EGLenum platform, void *native, const EGLint *attributes)',
 'extern "C" EGLDisplay eglGetPlatformDisplay(EGLenum platform, void *native, const EGLAttrib *attributes)']:
 anchor=signature+'\n{';assert bridge.count(anchor)==1
 bridge=bridge.replace(anchor,anchor+'\n    gpu892_trace("GPU894_PLATFORM api='+signature.split('(')[0].split()[-1]+' platform=%x native=%p first_attribute=%lx\\n",platform,native,attributes?(unsigned long)attributes[0]:0ul);')
old='if (AuroraOpenDisplayDrm(&display.drm, 0)) { error(EGL_NOT_INITIALIZED); return EGL_NO_DISPLAY; }'
assert bridge.count(old)==1
bridge=bridge.replace(old,'int drm_result=AuroraOpenDisplayDrm(&display.drm,0); gpu892_trace("GPU894_DRM rc=%d errno=%d fd=%d\\n",drm_result,errno,display.drm.fd); if(drm_result) { error(EGL_NOT_INITIALIZED);return EGL_NO_DISPLAY; }')
old='display.device = gbm_create_device(display.drm.fd);'
assert bridge.count(old)==1
bridge=bridge.replace(old,old+' gpu892_trace("GPU894_GBM device=%p errno=%d\\n",display.device,errno);')
old='display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);'
assert bridge.count(old)==1
bridge=bridge.replace(old,old+' gpu892_trace("GPU894_DISPLAY value=%p\\n",display.egl);')
old=' gpu892_trace("GPU888_CREATE_CONTEXT result=%p\\n",result);return result;'
assert bridge.count(old)==1
bridge=bridge.replace(old,' gpu892_trace("GPU894_CONTEXT d=%p config=%p shared=%p result=%p attrs=",d,c,s,result); if(a)for(unsigned i=0;i<32 && a[i]!=EGL_NONE;i+=2)gpu892_trace("%x:%x,",a[i],a[i+1]);gpu892_trace("\\n");return result;')
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17',
 '-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),
 '-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),
 str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl',
 '-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions',
 '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-894')
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)

"""Fresh 898: observe swap results and actual fbdev/DRM state, without bypassing drawing."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
out=base/'payload-898';assert not out.exists()
source=(base/'payload-897/init.c').read_text()
anchor='static void command_probe(void)'
assert source.count(anchor)==1
source=source.replace(anchor,'#include "gpu-present-snapshot.h"\n'+anchor)
anchor='    ui_snapshot();'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    gpu898_snapshot();')
source=source.replace('char trace_data[4097]','char trace_data[24001]')
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-898'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'gpu-present-snapshot.h'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script=r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'present-result-898';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'service-env-897/ramroot',ram,symlinks=True)
bridge=(root/'rendernode-trace-896/bridge.cpp').read_text()
changes={
'if (api->request(window->native, &buffer, &fence)) {':'int request_result=api->request(window->native,&buffer,&fence); gpu892_trace("GPU898_REQUEST rc=%d buffer=%p fence=%d\\n",request_result,buffer,fence); if(request_result) {',
'if (!waited || !valid(handle) || !copy_frame(*window, *handle)) {':'bool copied=waited && valid(handle) && copy_frame(*window,*handle); gpu892_trace("GPU898_COPY waited=%d copied=%d format=%d size=%dx%d\\n",waited,copied,handle?handle->format:-1,handle?handle->width:0,handle?handle->height:0); if(!copied) {',
'if (api->flush(window->native, buffer, -1, Region{nullptr, 0})) {':'int flush_result=api->flush(window->native,buffer,-1,Region{nullptr,0}); gpu892_trace("GPU898_FLUSH rc=%d\\n",flush_result); if(flush_result) {',
'if (!swap(egl, window->backing)) return EGL_FALSE;':'EGLBoolean swapped=swap(egl,window->backing); gpu892_trace("GPU898_SWAP result=%u\\n",swapped); if(!swapped)return EGL_FALSE;',
}
for old,new in changes.items():
 assert bridge.count(old)==1,old
 bridge=bridge.replace(old,new)
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-898')
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)

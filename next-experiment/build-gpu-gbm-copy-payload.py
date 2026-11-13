"""Fresh 912: GBM WSI upload and independent real-pixel NativeWindow fixture."""
from pathlib import Path
import subprocess
base = Path(__file__).resolve().parent
out = base/'payload-912'
assert not out.exists()
source = (base/'payload-907/init.c').read_text()
anchor = '    puts("GPU885_DONE desktop_not_tested=1");fflush(stdout);'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    pid_t window_test=fork();if(window_test<0)die("GPU912 fork");
    if(!window_test) {
      alarm(60);
      setenv("LD_LIBRARY_PATH","/system/lib64/lab-softpipe-167:/system/lib64:/system/lib64/platformsdk:/system/lib64/chipset-sdk:/vendor/lib64",1);
      setenv("GBM_BACKENDS_PATH","/system/lib64/lab-softpipe-167/gbm",1);
      execl("/system/lib64/lab-softpipe-167/gpu912-window-probe","gpu912-window-probe",NULL);
      perror("GPU912 exec");_exit(125);
    }
    int window_status=0;while(waitpid(window_test,&window_status,0)<0&&errno==EINTR){}
    printf("GPU912_WINDOW_STATUS status=%d desktop_not_assumed=1\n",window_status);fflush(stdout);
''' + anchor)
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-912'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),str(base/'bounded-shell.c'),str(base/'gpu-present-snapshot.h'),str(base/'payload-900/gpu-pixel-snapshot.h'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
setup=r'''
from pathlib import Path
import subprocess,shutil,runpy,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');work=root/'gbm-copy-912';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
reference=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports')
ram=work/'ramroot';shutil.copytree(root/'copy-error-911/ramroot',ram,symlinks=True)
out=local/'payload-912';shutil.copy2(out/'init',ram/'init')
transform=runpy.run_path(str(local/'gpu-gbm-copy.py'))['gbm_copy']
(work/'bridge.cpp').write_text(transform((root/'copy-error-911/bridge.cpp').read_text()))
previous=root/'window-bridge';prefix=root/'prefix/system';libs=prefix/'lib64/lab-virgl883'
cxx=previous/'toolchain/ohos-platform-cxx'
with (work/'build.log').open('w') as log:
 subprocess.run([str(cxx),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),str(previous/'drm_device.o'),'-L'+str(libs),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
 probe=(reference/'tests/egl-window-probe.cpp').read_text().replace('/vendor/lib64/aurora-graphics/libdisplay_buffer_vdi_impl.z.so','/system/lib64/lab-softpipe-167/gpu905-buffer-vdi.so')
 probe=probe.replace('< rendered_height / 2;', '< uint64_t(rendered_height / 2);')
 (work/'probe.cpp').write_text(probe)
 subprocess.run([str(cxx),'-O2','-std=c++17','-Wall','-Wextra','-Werror','-DEGL_EGLEXT_PROTOTYPES','-isystem',str(previous/'include'),'-I'+str(prefix/'include'),str(work/'probe.cpp'),'-L'+str(ram/'gpu883-libs'),'-l:libEGL_impl.so','-L'+str(libs),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--export-dynamic','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/gpu912-window-probe')],stdout=log,stderr=subprocess.STDOUT,check=True)
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
archive=archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe','gpu912-window-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=setup+archive,text=True,check=True)

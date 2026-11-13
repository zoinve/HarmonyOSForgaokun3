"""Fresh 903: compare original and DRM VDI on own buffers, without service replacement."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-903'
assert not out.exists()
source = (base / 'payload-900/init.c').read_text()
anchor = '    puts("GPU885_DONE desktop_not_tested=1");fflush(stdout);'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
    const char *allocators[]={"/vendor/lib64/libdisplay_buffer_vdi_impl.z.so",
        "/system/lib64/lab-softpipe-167/gpu903-buffer-vdi.so"};
    for(unsigned i=0;i<2;i++) {
      pid_t p=fork();if(p<0)die("GPU903 fork");
      if(!p) {
        alarm(30);
        setenv("LD_LIBRARY_PATH","/system/lib64/lab-softpipe-167:/system/lib64:/system/lib64/platformsdk:/system/lib64/chipset-sdk:/vendor/lib64",1);
        setenv("GBM_BACKENDS_PATH","/system/lib64/lab-softpipe-167/gbm",1);
        execl("/system/lib64/lab-softpipe-167/gpu903-allocator-probe","gpu903-allocator-probe",allocators[i],NULL);
        perror("GPU903 exec");_exit(125);
      }
      int status=0;while(waitpid(p,&status,0)<0&&errno==EINTR){}
      printf("GPU903_CHILD allocator=%s status=%d\n",allocators[i],status);fflush(stdout);
    }
''' + anchor)
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-903'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir()
(out/'init.c').write_text(source)
subprocess.run(['scp',str(out/'init.c'),*[str(base/p) for p in
    ['bounded-shell.c','gpu-present-snapshot.h','payload-900/gpu-pixel-snapshot.h']], 'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script = r'''
from pathlib import Path
import subprocess,shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'allocator-probe-903';work.mkdir()
reference=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports')
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
ram=work/'ramroot';shutil.copytree(root/'buffer-import-902/ramroot',ram,symlinks=True)
out=local/'payload-903';shutil.copy2(out/'init',ram/'init')
shutil.copytree(reference/'graphics/include',work/'include')
shutil.copy2(reference/'graphics/buffer_vdi.cpp',work/'buffer_vdi.cpp')
shutil.copy2(reference/'graphics/drm_device.c',work/'drm_device.c')
shutil.copy2(local/'gpu-runtime-883/original-real-buffer-handle-903.so',work/'libbuffer_handle.z.so')
prefix=root/'prefix/system';libs=prefix/'lib64/lab-virgl883'
includes=['-isystem',str(work/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
cc=root/'toolchain/ohos-cc';cxx=root/'window-bridge/toolchain/ohos-platform-cxx'
subprocess.run([str(cc),'-O2','-fPIC','-Wall','-Wextra','-Werror',*includes,'-c',str(work/'drm_device.c'),'-o',str(work/'drm_device.o')],check=True)
common=[str(cxx),'-O2','-std=c++17','-Wall','-Wextra',*includes]
with (work/'build.log').open('w') as log:
 subprocess.run([*common,'-shared','-fPIC',str(work/'buffer_vdi.cpp'),str(work/'drm_device.o'),
  '-L'+str(libs),'-ldrm',str(work/'libbuffer_handle.z.so'),'-Wl,--no-undefined,-soname,gpu903-buffer-vdi.so',
  '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'gpu903-buffer-vdi.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run([*common,'-Werror',str(local/'gpu-allocator-probe.cpp'),str(work/'drm_device.o'),
  '-L'+str(libs),'-lEGL','-lGLESv2','-lgbm','-ldrm','-ldl',
  '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(work/'gpu903-allocator-probe')],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ['gpu903-buffer-vdi.so','gpu903-allocator-probe']:
 shutil.copy2(work/name,ram/'gpu883-libs'/name)
'''
original = (base/'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(',1)[1].split("'''",1)[0]
archive = archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)

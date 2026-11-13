"""Fresh 900: observe real GPU readback and Composer client pixels, no drawing changes."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
out=base/'payload-900';assert not out.exists()
header=(base/'gpu-composer-snapshot.h').read_text()
header='#include <sys/syscall.h>\n#include <sys/mman.h>\n'+header
old='fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0){printf("GPU899_CLIENT_OPEN errno=%d\\n",errno);continue;}'
new=r'''fd=open(path,O_RDONLY|O_CLOEXEC);
            if(fd<0) {
                int pfd=(int)syscall(SYS_pidfd_open,atoi(de->d_name),0);
                int pe=errno;
                fd=pfd>=0?(int)syscall(SYS_pidfd_getfd,pfd,client[0],0):-1;
                printf("GPU900_CLIENT_DUP pidfd=%d pid_errno=%d fd=%d errno=%d\n",pfd,pfd<0?pe:0,fd,fd<0?errno:0);
                if(pfd>=0)close(pfd);
            }
            if(fd<0)continue;
            size_t length=(size_t)client[3]*client[2];
            if(length<=64*1024*1024) {
                unsigned char *data=mmap(NULL,length,PROT_READ,MAP_SHARED,fd,0);
                if(data!=MAP_FAILED) {
                    unsigned long rgb=0;
                    for(int y=0;y<client[2];y++)for(int x=0;x<client[1];x++) {
                        size_t at=(size_t)y*client[3]+(size_t)x*4;
                        if(at+2<length&&(data[at]||data[at+1]||data[at+2]))rgb++;
                    }
                    printf("GPU900_CLIENT_PIXELS nonblack=%lu size=%dx%d cpu_sync_not_requested=1\n",rgb,client[1],client[2]);
                    munmap(data,length);
                } else printf("GPU900_CLIENT_MMAP errno=%d\n",errno);
            }'''
assert header.count(old)==1
header=header.replace(old,new)
source=(base/'payload-899/init.c').read_text()
assert source.count('#include "gpu-composer-snapshot.h"')==1
source=source.replace('#include "gpu-composer-snapshot.h"','#include "gpu-pixel-snapshot.h"')
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-900'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'init.c').write_text(source);(out/'gpu-pixel-snapshot.h').write_text(header)
subprocess.run(['scp',str(out/'init.c'),str(out/'gpu-pixel-snapshot.h'),str(base/'gpu-present-snapshot.h'),str(base/'bounded-shell.c'),'matebook:'+remote+'/'],check=True)
subprocess.run(['ssh','matebook',f'gcc -static -O2 -Wall -Wextra -Werror {remote}/init.c -o {remote}/init'],check=True)
subprocess.run(['scp','matebook:'+remote+'/init',str(out/'init')],check=True)
script=r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'pixel-trace-900';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'composer-snapshot-899/ramroot',ram,symlinks=True)
bridge=(root/'present-result-898/bridge.cpp').read_text()
bridge=bridge.replace('namespace {','static void gpu892_trace(const char *, ...);\nnamespace {',1)
old='    glFinish();\n    glPixelStorei(GL_PACK_ALIGNMENT, pack);'
new=r"""    glFinish();
    static unsigned observed=0;
    if(observed++<3) {
        size_t nonblack=0;
        for(size_t i=0;i+3<pixels.size();i+=4)if(pixels[i]||pixels[i+1]||pixels[i+2])nonblack++;
        size_t c=(size_t(window.height/2)*window.width+window.width/2)*4;
        gpu892_trace("GPU900_READBACK nonblack=%zu size=%dx%d center=%u,%u,%u,%u previous_fbo=%d es3=%d\n",nonblack,window.width,window.height,pixels[c],pixels[c+1],pixels[c+2],pixels[c+3],framebuffer,es3);
    }
    glPixelStorei(GL_PACK_ALIGNMENT, pack);"""
assert bridge.count(old)==1
bridge=bridge.replace(old,new)
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-900')
shutil.copy2(out/'init',ram/'init')
'''
original=(base/'build-gpu-frontend-payload.py').read_text()
archive='def entry('+original.split('def entry(',1)[1].split("'''",1)[0]
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)

"""Fresh 908: trace service allocator calls; no allocation-policy changes."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base/'payload-908'; assert not out.exists(); out.mkdir()
script = r'''
from pathlib import Path
import subprocess,shutil,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');work=root/'allocator-trace-908';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-908'
ram=work/'ramroot';shutil.copytree(root/'allocator-overlay-907/ramroot',ram,symlinks=True)
old=root/'gbm-vdi-905'
source=(old/'buffer_vdi.cpp').read_text().replace('#include <cstdlib>','#include <cstdlib>\n#include <cstdarg>')
a=source.index('#define AURORA_VDI_LOG(');b=source.index('/* Log the direct caller',a)
source=source[:a]+r"""
static void gpu908_log(const char *fmt, ...) {
    static unsigned count=0; if(count++>=160)return;
    int saved=errno;char path[128];snprintf(path,sizeof(path),"/dev/gpu893-trace/gpu908-%d.log",getpid());
    int fd=open(path,O_WRONLY|O_APPEND|O_CREAT|O_CLOEXEC|O_NOFOLLOW,0600);
    if(fd>=0){FILE *f=fdopen(fd,"a");if(f){va_list args;va_start(args,fmt);vfprintf(f,fmt,args);va_end(args);fputc('\n',f);fclose(f);}else close(fd);}
    errno=saved;
}
#define AURORA_VDI_LOG(...) gpu908_log(__VA_ARGS__)
"""+source[b:]
source=source.replace('if (display_.fd < 0 && AuroraOpenDisplayDrm(&display_, 0)) return false;',
    'if (display_.fd < 0 && AuroraOpenDisplayDrm(&display_, 0)) { AURORA_VDI_LOG("DRM_OPEN_FAIL errno=%d",errno); return false; }')
source=source.replace('gbm_ = gbm_create_device(display_.fd); return gbm_ != nullptr;',
    'gbm_ = gbm_create_device(display_.fd); AURORA_VDI_LOG("GBM_DEVICE fd=%d device=%p errno=%d",display_.fd,(void*)gbm_,errno); return gbm_ != nullptr;')
source=source.replace('if (!bo) return -1;', 'if (!bo) { AURORA_VDI_LOG("BO_CREATE_FAIL errno=%d",errno); return -1; }')
source=source.replace('if (fd < 0) return -1;', 'if (fd < 0) { AURORA_VDI_LOG("EXPORT_FAIL errno=%d",errno); return -1; }')
source=source.replace('if (bytes > INT_MAX || bytes < info.expectedSize) { close(fd); return NOT_SUPPORT; }',
    'if (bytes > INT_MAX || bytes < info.expectedSize) { AURORA_VDI_LOG("SIZE_REJECT actual=%llu expected=%llu",(unsigned long long)bytes,(unsigned long long)info.expectedSize); close(fd); return NOT_SUPPORT; }')
source=source.replace('BufferHandle *abi = AllocateBufferHandle(2, 3);',
    'AURORA_VDI_LOG("FACTORY uid=%d gid=%d",getuid(),getgid()); BufferHandle *abi = AllocateBufferHandle(2, 3);')
(work/'buffer_vdi.cpp').write_text(source)
prefix=root/'prefix/system';libs=prefix/'lib64/lab-virgl883';cxx=root/'window-bridge/toolchain/ohos-platform-cxx'
with (work/'build.log').open('w') as log:
 subprocess.run([str(cxx),'-O2','-std=c++17','-Wall','-Wextra','-isystem',str(old/'include'),
  '-I'+str(old),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),'-shared','-fPIC',str(work/'buffer_vdi.cpp'),str(old/'drm_device.o'),
  '-L'+str(libs),'-lgbm','-ldrm',str(old/'libbuffer_handle.z.so'),'-Wl,--no-undefined,-soname,gpu905-buffer-vdi.so',
  '-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/gpu905-buffer-vdi.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
'''
original = (base/'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(',1)[1].split("'''",1)[0]
archive = archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)

"""Fresh 911: record presentation mapping/sync failures without changing returns."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-911'
assert not out.exists()
out.mkdir()
setup = r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'copy-error-911';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'driver-rpath-910/ramroot',ram,symlinks=True)
bridge=(root/'image-trace-901/bridge.cpp').read_text()
old='    if (memory == MAP_FAILED) return false;'
new='    if (memory == MAP_FAILED) { gpu901_image("GPU911_COPY_FAIL stage=mmap fd=%d size=%d errno=%d\\n",buffer.fd,buffer.size,errno); return false; }'
assert bridge.count(old)==1
bridge=bridge.replace(old,new)
old='    if (ioctl(buffer.fd, DMA_BUF_IOCTL_SYNC, &sync)) { munmap(memory, buffer.size); return false; }'
new='    if (ioctl(buffer.fd, DMA_BUF_IOCTL_SYNC, &sync)) { gpu901_image("GPU911_COPY_FAIL stage=sync_start fd=%d errno=%d\\n",buffer.fd,errno); munmap(memory, buffer.size); return false; }'
assert bridge.count(old)==1
bridge=bridge.replace(old,new)
old='    int result = ioctl(buffer.fd, DMA_BUF_IOCTL_SYNC, &sync);'
new=old+'\n    if(result) gpu901_image("GPU911_COPY_FAIL stage=sync_end fd=%d errno=%d\\n",buffer.fd,errno);'
assert bridge.count(old)==1
bridge=bridge.replace(old,new)
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-911')
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
archive = archive.replace("p.name=='gpu-frontend-probe'", "p.name in ('gpu-frontend-probe','gpu903-allocator-probe')")
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=setup + archive, text=True, check=True)

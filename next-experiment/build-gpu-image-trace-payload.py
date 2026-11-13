"""Fresh 901: observe real image imports and later readbacks; no rendering changes."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-901'
assert not out.exists()
out.mkdir()
setup = r'''
from pathlib import Path
import shutil,gzip,hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'image-trace-901';work.mkdir()
ram=work/'ramroot';shutil.copytree(root/'pixel-trace-900/ramroot',ram,symlinks=True)
bridge=(root/'pixel-trace-900/bridge.cpp').read_text()
helper=r"""
static void gpu901_image(const char *format, ...)
{
    int saved=errno;
    static unsigned count=0;
    if(__atomic_fetch_add(&count,1,__ATOMIC_RELAXED)<100) {
        char path[128];snprintf(path,sizeof(path),"/dev/gpu893-trace/gpu901-%d.log",getpid());
        int fd=open(path,O_WRONLY|O_CREAT|O_APPEND|O_CLOEXEC|O_NOFOLLOW,0600);
        if(fd>=0) {
            FILE *file=fdopen(fd,"a");
            if(file){va_list args;va_start(args,format);vfprintf(file,format,args);va_end(args);fclose(file);}
            else close(fd);
        }
    }
    errno=saved;
}
"""
anchor='static void gpu892_trace(const char *, ...);'
assert bridge.count(anchor)==2
bridge=bridge.replace(anchor,anchor+'\n'+helper,1)
anchor='    if (target != NATIVE_BUFFER_OHOS) return fn(egl, context, target, object, attributes);'
replacement=r"""    gpu901_image("GPU901_IMAGE_ENTER target=%x context=%p object=%p\n",target,context,object);
    if (target != NATIVE_BUFFER_OHOS) {
        EGLImageKHR result=fn(egl,context,target,object,attributes);
        gpu901_image("GPU901_IMAGE_OTHER target=%x result=%p\n",target,result);
        return result;
    }"""
assert bridge.count(anchor)==1
bridge=bridge.replace(anchor,replacement)
anchor='    if (!valid(handle)) { error(EGL_BAD_PARAMETER); return EGL_NO_IMAGE_KHR; }'
replacement=r"""    gpu901_image("GPU901_NATIVE_BUFFER handle=%p valid=%d fd=%d size=%dx%d stride=%d format=%d\n",handle,valid(handle),handle?handle->fd:-1,handle?handle->width:0,handle?handle->height:0,handle?handle->stride:0,handle?handle->format:-1);
    if (!valid(handle)) { error(EGL_BAD_PARAMETER); return EGL_NO_IMAGE_KHR; }"""
assert bridge.count(anchor)==1
bridge=bridge.replace(anchor,replacement)
anchor='    return fn(egl, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, attrs);'
replacement=r"""    EGLImageKHR result=fn(egl, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, attrs);
    gpu901_image("GPU901_IMAGE_IMPORT result=%p fd=%d drm_format=%x\n",result,handle->fd,format);
    return result;"""
assert bridge.count(anchor)==1
bridge=bridge.replace(anchor,replacement)
bridge=bridge.replace('if(observed++<3) {','if(++observed<=3 || observed%120==0) {')
bridge=bridge.replace('gpu892_trace("GPU900_READBACK','gpu901_image("GPU900_READBACK')
(work/'bridge.cpp').write_text(bridge)
previous=root/'window-bridge';prefix=root/'prefix/system'
with (work/'build.log').open('w') as log:
 subprocess.run([str(previous/'toolchain/ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES','-I'+str(previous),'-I'+str(previous/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'bridge.cpp'),str(previous/'drm_device.o'),'-L'+str(prefix/'lib64/lab-virgl883'),'-lGLESv2','-lgbm','-ldrm','-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-softpipe-167','-o',str(ram/'gpu883-libs/libEGL_impl.so')],stdout=log,stderr=subprocess.STDOUT,check=True)
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/payload-901')
'''
original = (base / 'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(', 1)[1].split("'''", 1)[0]
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
               input=setup + archive, text=True, check=True)

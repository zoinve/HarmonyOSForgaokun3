"""Compare GPU-native GBM allocation with failed dumb-buffer DMA imports."""
from pathlib import Path
import subprocess
payload=r"""
from pathlib import Path
import subprocess
r=Path('/home/zoinve/harmony-virgl-883');w=r/'native-gpu-probe-040';w.mkdir(exist_ok=False)
s=(r/'native-gpu-probe-037/gpu-probe-037.c').read_text()
s=s.replace('EGLImageKHR egl; };','EGLImageKHR egl;struct gbm_bo *bo; };',1)
start=s.index('static struct image make_image(');end=s.index('static GLuint shader(',start)
s=s[:start]+'''static struct gbm_device *gpu_device;
static struct gbm_bo *(*bo_create)(struct gbm_device*,uint32_t,uint32_t,uint32_t,uint32_t);
static int (*bo_fd)(struct gbm_bo*);
static uint32_t (*bo_stride)(struct gbm_bo*);
static void (*bo_destroy)(struct gbm_bo*);
static struct image make_image(unsigned width,unsigned height,unsigned fourcc)
{
 struct gbm_bo *bo=bo_create(gpu_device,width,height,fourcc,GBM_BO_USE_LINEAR|GBM_BO_USE_RENDERING|GBM_BO_USE_SCANOUT);assert(bo);
 int fd=bo_fd(bo);assert(fd>=0);unsigned pitch=bo_stride(bo);off_t size=lseek(fd,0,SEEK_END);assert(size>0);
 unsigned char *map=mmap(NULL,(size_t)size,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);assert(map!=MAP_FAILED);
 EGLint a[]={EGL_WIDTH,(EGLint)width,EGL_HEIGHT,(EGLint)height,EGL_LINUX_DRM_FOURCC_EXT,(EGLint)fourcc,
  EGL_DMA_BUF_PLANE0_FD_EXT,fd,EGL_DMA_BUF_PLANE0_OFFSET_EXT,0,EGL_DMA_BUF_PLANE0_PITCH_EXT,(EGLint)pitch,EGL_NONE};
 EGLImageKHR e=create_image(display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,a);assert(e!=EGL_NO_IMAGE_KHR);
 printf("GBM import width=%u height=%u pitch=%u size=%lld\\n",width,height,pitch,(long long)size);
 return (struct image){width,height,pitch,0,fd,(size_t)size,map,e,bo};
}
static void free_image(struct image *i)
{assert(destroy_image(display,i->egl));assert(!munmap(i->map,i->size));assert(!close(i->fd));bo_destroy(i->bo);}
''' +s[end:]
anchor='display=platform(EGL_PLATFORM_GBM_KHR,device,NULL);'
assert s.count(anchor)==1
s=s.replace(anchor,'''gpu_device=device;bo_create=(void*)required(gbm,"gbm_bo_create");bo_fd=(void*)required(gbm,"gbm_bo_get_fd");
 bo_stride=(void*)required(gbm,"gbm_bo_get_stride");bo_destroy=(void*)required(gbm,"gbm_bo_destroy");
 '''+anchor,1)
(w/'gpu-probe-040.c').write_text(s)
subprocess.run(['aarch64-linux-gnu-gcc','-O2','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror',
 '-I'+str(r/'prefix/system/include'),'-I'+str(r/'prefix/system/include/libdrm'),str(w/'gpu-probe-040.c'),'-ldl','-o',str(w/'gpu-probe')],check=True)
print('PASS: GBM allocation comparison probe 040 compiled; no pipeline deployed')
"""
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

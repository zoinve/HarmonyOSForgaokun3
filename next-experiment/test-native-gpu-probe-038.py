"""Collect the exact 037 DMA import error and format capabilities; do not guess a fix."""
from pathlib import Path
import subprocess
payload=r"""
from pathlib import Path
import subprocess
r=Path('/home/zoinve/harmony-virgl-883');w=r/'native-gpu-probe-038';w.mkdir(exist_ok=False)
s=(r/'native-gpu-probe-037/gpu-probe-037.c').read_text()
old='EGLImageKHR e=create_image(display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,a);assert(e!=EGL_NO_IMAGE_KHR);'
assert s.count(old)==1
s=s.replace(old,'''EGLImageKHR e=create_image(display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,NULL,a);
 if(e==EGL_NO_IMAGE_KHR){PFNEGLGETERRORPROC error=(void*)getproc("eglGetError");fprintf(stderr,"DMA import failed EGL=0x%x width=%u height=%u pitch=%u format=0x%x fd=%d size=%llu\\n",error?error():0,width,height,c.pitch,fourcc,p.fd,(unsigned long long)c.size);exit(6);}''',1)
anchor='assert(renderer&&strstr(renderer,"FD690"));GLuint prog=program();'
assert s.count(anchor)==1
s=s.replace(anchor,'''assert(renderer&&strstr(renderer,"FD690"));
 PFNEGLQUERYSTRINGPROC query=(void*)getproc("eglQueryString");printf("EGL extensions=%s\\n",query(display,EGL_EXTENSIONS));
 PFNEGLQUERYDMABUFFORMATSEXTPROC formats=(void*)getproc("eglQueryDmaBufFormatsEXT");
 EGLint total=0;if(formats&&formats(display,0,NULL,&total)){EGLint *f=calloc((size_t)total,sizeof(*f));assert(f);assert(formats(display,total,f,&total));for(int n=0;n<total;++n)printf("DMA format=0x%x\\n",f[n]);free(f);}
 GLuint prog=program();''',1)
(w/'gpu-probe-038.c').write_text(s)
subprocess.run(['aarch64-linux-gnu-gcc','-O2','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror',
 '-I'+str(r/'prefix/system/include'),'-I'+str(r/'prefix/system/include/libdrm'),str(w/'gpu-probe-038.c'),'-ldl','-o',str(w/'gpu-probe')],check=True)
print('PASS: diagnostic 038 compiled; no import repair applied')
"""
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

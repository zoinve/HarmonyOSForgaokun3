"""Confirm pixel writes without consuming GL errors or changing rendered content."""
from pathlib import Path
import runpy
previous=runpy.run_path(str(Path(__file__).with_name('commercial-gl-dispatch-033.py')))
PROBE=r'''
struct Readback035 { bool complete=false; unsigned attempted=0,confirmed=0,nonblack=0; };
static Readback035 sample035(GLuint framebuffer,GLenum buffer,int width,int height){
 const int saved_errno035=errno;Readback035 result;
 if(width<=0 || height<=0)return result;
 GLint old_fbo=0,old_buffer=0,target_buffer=0,pack=0,alignment=0,row=0,skipx=0,skipy=0;
 glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&old_fbo);glGetIntegerv(GL_READ_BUFFER,&old_buffer);
 glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&pack);glGetIntegerv(GL_PACK_ALIGNMENT,&alignment);
 glGetIntegerv(GL_PACK_ROW_LENGTH,&row);glGetIntegerv(GL_PACK_SKIP_PIXELS,&skipx);glGetIntegerv(GL_PACK_SKIP_ROWS,&skipy);
 glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer);glGetIntegerv(GL_READ_BUFFER,&target_buffer);
 result.complete=glCheckFramebufferStatus(GL_READ_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE;
 if(result.complete){
  glReadBuffer(buffer);glBindBuffer(GL_PIXEL_PACK_BUFFER,0);
  glPixelStorei(GL_PACK_ALIGNMENT,1);glPixelStorei(GL_PACK_ROW_LENGTH,0);
  glPixelStorei(GL_PACK_SKIP_PIXELS,0);glPixelStorei(GL_PACK_SKIP_ROWS,0);
  for(int y=0;y<3;++y)for(int x=0;x<3;++x){
   unsigned char first[4]={0x19,0x37,0x5b,0x7d},second[4]={0xe6,0xc8,0xa4,0x82};
   glReadPixels((2*x+1)*width/6,(2*y+1)*height/6,1,1,GL_RGBA,GL_UNSIGNED_BYTE,first);
   glReadPixels((2*x+1)*width/6,(2*y+1)*height/6,1,1,GL_RGBA,GL_UNSIGNED_BYTE,second);
   ++result.attempted;
   bool same=true;for(unsigned c=0;c<4;++c)if(first[c]!=second[c])same=false;
   if(same){++result.confirmed;if(first[0] || first[1] || first[2])++result.nonblack;}
  }
 }
 glReadBuffer(GLenum(target_buffer));glBindFramebuffer(GL_READ_FRAMEBUFFER,GLuint(old_fbo));glReadBuffer(GLenum(old_buffer));
 glBindBuffer(GL_PIXEL_PACK_BUFFER,GLuint(pack));glPixelStorei(GL_PACK_ALIGNMENT,alignment);
 glPixelStorei(GL_PACK_ROW_LENGTH,row);glPixelStorei(GL_PACK_SKIP_PIXELS,skipx);glPixelStorei(GL_PACK_SKIP_ROWS,skipy);
 errno=saved_errno035;return result;
}
'''
LOG=r'''
static int probe031(GLuint framebuffer,GLenum buffer,int width,int height){
 const int saved035=errno;
 auto r035=sample035(framebuffer,buffer,width,height);
 using Print035=int (*)(int,int,unsigned,const char *,const char *,...);
 static auto print035=reinterpret_cast<Print035>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
 if(print035)print035(3,4,0x0D002510,"CommercialReadback035",
  "READBACK035 framebuffer=%{public}u buffer=%{public}u width=%{public}d height=%{public}d complete=%{public}d attempted=%{public}u confirmed=%{public}u nonblack=%{public}u error_not_consumed=1",
  framebuffer,buffer,width,height,int(r035.complete),r035.attempted,r035.confirmed,r035.nonblack);
 errno=saved035;
 return r035.confirmed==9?int(r035.nonblack):-2;
}
static void config035(const Window &window){
 const int saved035=errno;EGLint samples035=-1,buffers035=-1;
 auto get035=real<decltype(&eglGetConfigAttrib)>("eglGetConfigAttrib");
 EGLBoolean samples_ok035=EGL_FALSE,buffers_ok035=EGL_FALSE;
 if(get035){samples_ok035=get035(window.display,window.config,EGL_SAMPLES,&samples035);
  buffers_ok035=get035(window.display,window.config,EGL_SAMPLE_BUFFERS,&buffers035);}
 using Print035=int (*)(int,int,unsigned,const char *,const char *,...);
 static auto print035=reinterpret_cast<Print035>(dlsym(RTLD_DEFAULT,"HiLogPrint"));
 if(print035)print035(3,4,0x0D002510,"CommercialReadback035",
  "CONFIG035 samples_ok=%{public}d samples=%{public}d buffers_ok=%{public}d sample_buffers=%{public}d width=%{public}d height=%{public}d error_not_consumed=1",
  int(samples_ok035),samples035,int(buffers_ok035),buffers035,window.width,window.height);
 errno=saved035;
}
'''

def instrument(source):
 result=previous['instrument'](source)
 old=previous['previous']['PROBE']
 assert result.count(old)==1 and 'READBACK035' not in result
 result=result.replace(old,PROBE+LOG,1)
 anchor='            if(observe031){\n'
 assert result.count(anchor)==1
 return result.replace(anchor,anchor+'                config035(window);\n',1)

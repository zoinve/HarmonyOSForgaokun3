"""Observe actual default and destination framebuffer RGB; never draw test content."""
from pathlib import Path
import runpy,hashlib
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'commercial-egl-trace-029.py'))
COPY=(base/'native-gpu-copy-025.h').read_text()
assert hashlib.sha256((base/'native-gpu-copy-025.h').read_bytes()).hexdigest()=='7fe12e2ad194a6968938ab6a92f1d147b7f9ef69c6b3878081887aa116958f8c'
PROBE=r'''
static int probe031(GLuint framebuffer,GLenum buffer,int width,int height){
 const int saved_errno031=errno;
 if(width<=0 || height<=0)return -1;
 GLint old_fbo=0,old_buffer=0,target_buffer=0,pack=0,alignment=0,row=0,skipx=0,skipy=0;
 glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&old_fbo);glGetIntegerv(GL_READ_BUFFER,&old_buffer);
 glGetIntegerv(GL_PIXEL_PACK_BUFFER_BINDING,&pack);glGetIntegerv(GL_PACK_ALIGNMENT,&alignment);
 glGetIntegerv(GL_PACK_ROW_LENGTH,&row);glGetIntegerv(GL_PACK_SKIP_PIXELS,&skipx);glGetIntegerv(GL_PACK_SKIP_ROWS,&skipy);
 glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer);glGetIntegerv(GL_READ_BUFFER,&target_buffer);
 int nonblack=-1;
 if(glCheckFramebufferStatus(GL_READ_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE){
  glReadBuffer(buffer);glBindBuffer(GL_PIXEL_PACK_BUFFER,0);
  glPixelStorei(GL_PACK_ALIGNMENT,1);glPixelStorei(GL_PACK_ROW_LENGTH,0);
  glPixelStorei(GL_PACK_SKIP_PIXELS,0);glPixelStorei(GL_PACK_SKIP_ROWS,0);
  nonblack=0;
  for(int y=0;y<3;++y)for(int x=0;x<3;++x){
   unsigned char pixel[4]={};
   glReadPixels((2*x+1)*width/6,(2*y+1)*height/6,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
   if(pixel[0] || pixel[1] || pixel[2])++nonblack;
  }
 }
 glReadBuffer(GLenum(target_buffer));glBindFramebuffer(GL_READ_FRAMEBUFFER,GLuint(old_fbo));glReadBuffer(GLenum(old_buffer));
 glBindBuffer(GL_PIXEL_PACK_BUFFER,GLuint(pack));glPixelStorei(GL_PACK_ALIGNMENT,alignment);
 glPixelStorei(GL_PACK_ROW_LENGTH,row);glPixelStorei(GL_PACK_SKIP_PIXELS,skipx);glPixelStorei(GL_PACK_SKIP_ROWS,skipy);
 errno=saved_errno031;return nonblack;
}
'''
stages=previous['stages']+['copy-default-nonblack','copy-destination-nonblack','copy-read-fbo','copy-draw-fbo']
HEADER=previous['HEADER'].replace('029','031').replace('calls[22]','calls[26]').replace('slot<22','slot<26')
old=','.join('"'+s+'"' for s in previous['stages'])
assert HEADER.count(old)==1
HEADER=HEADER.replace(old,','.join('"'+s+'"' for s in stages),1)

def instrument_copy(source):
    assert source.count('static bool copy_frame_gpu_025(')==1
    anchor='            glBlitFramebuffer(0,0,window.width,window.height,0,buffer.height,buffer.width,0,GL_COLOR_BUFFER_BIT,GL_NEAREST);'
    assert source.count(anchor)==1
    assert 'probe031(' not in source
    observation='''            static unsigned count031=0;
            bool observe031=__atomic_fetch_add(&count031,1u,__ATOMIC_RELAXED)<8;
            if(observe031){
                trace031("copy-read-fbo",saved_read);trace031("copy-draw-fbo",saved_draw);
                trace031("copy-default-nonblack",probe031(0,GL_BACK,window.width,window.height));
            }
'''+anchor+'''
            if(observe031)trace031("copy-destination-nonblack",probe031(fbo,GL_COLOR_ATTACHMENT0,buffer.width,buffer.height));'''
    return PROBE+source.replace(anchor,observation,1)

def instrument(source):
    result=previous['instrument'](source)
    assert result.count(previous['HEADER'])==1
    result=result.replace(previous['HEADER'],HEADER,1).replace('trace029','trace031').replace('drm_result029','drm_result031')
    anchor='#include "native-gpu-copy-025.h"'
    assert result.count(anchor)==1
    return result.replace(anchor,instrument_copy(COPY),1)

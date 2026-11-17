"""A no-write GL read must never be classified as a confirmed black pixel."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
assert (b/'commercial-readback-035.py').is_file(),'missing confirmed readback observation'
p=runpy.run_path(str(b/'commercial-readback-035.py'))
fixture=r'''
#include <cerrno>
#include <cassert>
using GLint=int;using GLuint=unsigned;using GLenum=unsigned;
enum {GL_READ_FRAMEBUFFER_BINDING=1,GL_READ_BUFFER,GL_PIXEL_PACK_BUFFER_BINDING,GL_PACK_ALIGNMENT,GL_PACK_ROW_LENGTH,GL_PACK_SKIP_PIXELS,GL_PACK_SKIP_ROWS,GL_READ_FRAMEBUFFER,GL_PIXEL_PACK_BUFFER,GL_FRAMEBUFFER_COMPLETE,GL_RGBA,GL_UNSIGNED_BYTE};
static int state[8]={0,42,99,7,8,9,10,11};static int mode=0,reads=0;static bool complete=true;
static void glGetIntegerv(unsigned k,int *v){*v=state[k];}
static void glBindFramebuffer(unsigned,unsigned v){state[1]=v;}
static void glReadBuffer(unsigned v){state[2]=v;}
static void glBindBuffer(unsigned,unsigned v){state[3]=v;}
static void glPixelStorei(unsigned k,int v){state[k]=v;}
static unsigned glCheckFramebufferStatus(unsigned){return complete?GL_FRAMEBUFFER_COMPLETE:0;}
static void glReadPixels(int x,int y,int w,int h,unsigned format,unsigned type,void *ptr){
 assert(x>=0 && x<2560 && y>=0 && y<1600 && w==1 && h==1 && format==GL_RGBA && type==GL_UNSIGNED_BYTE);
 ++reads;errno=99;auto p=static_cast<unsigned char*>(ptr);
 if(mode==0)return;
 if(mode==3){p[0]=13;return;}
 p[0]=mode==2?13:0;p[1]=p[2]=0;p[3]=255;
}
'''+p['PROBE']+r'''
int main(){
 int old[8];for(int i=0;i<8;++i)old[i]=state[i];errno=17;
 for(int m=0;m<4;++m){mode=m;auto r=sample035(5,12,2560,1600);
  assert(errno==17);for(int i=0;i<8;++i)assert(old[i]==state[i]);
  assert(r.attempted==9);
  if(m==0 || m==3){assert(r.confirmed==0 && r.nonblack==0);}
  else {assert(r.confirmed==9 && r.nonblack==(m==2?9:0));}
 }
 assert(reads==72);complete=false;auto bad=sample035(5,12,2560,1600);
 assert(!bad.complete && bad.attempted==0 && reads==72 && errno==17);
 for(int i=0;i<8;++i)assert(old[i]==state[i]);
 auto zero=sample035(5,12,0,1600);assert(zero.attempted==0 && errno==17);
}
'''
remote='import pathlib,tempfile,subprocess\ncode='+repr(fixture)+'''
with tempfile.TemporaryDirectory(prefix='readback035-') as d:
 p=pathlib.Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=60)
remote=r'''
from pathlib import Path
import runpy
p=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/commercial-readback-035.py')
source=Path('/home/zoinve/harmony-virgl-883/commercial-graphics-014/egl-commercial-014.cpp').read_text()
old=p['previous']['instrument'](source);new=p['instrument'](source)
recovered=new.replace(p['PROBE']+p['LOG'],p['previous']['previous']['PROBE'],1).replace('                config035(window);\n','',1)
assert recovered==old
assert new.count('glBlitFramebuffer(')==old.count('glBlitFramebuffer(')==1
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=30)
for forbidden in ['glGetError','eglGetError','glDraw','glClear']:
 assert forbidden not in p['PROBE'],forbidden
print('PASS: no-write and partial-write readbacks remain unconfirmed; black/color, GL state and errno verified')

"""Native state-restoration fixture; not actual target rendering evidence."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-egl-pixels-031.py').exists(),'missing bounded EGL pixel probe'
p=runpy.run_path(str(base/'commercial-egl-pixels-031.py'))
code=r'''
#include <cerrno>
#include <cstdint>
#include <cstdio>
using GLint=int;using GLuint=unsigned;using GLenum=unsigned;
enum {GL_READ_FRAMEBUFFER_BINDING=1,GL_READ_BUFFER,GL_PIXEL_PACK_BUFFER_BINDING,GL_PACK_ALIGNMENT,GL_PACK_ROW_LENGTH,GL_PACK_SKIP_PIXELS,GL_PACK_SKIP_ROWS,GL_READ_FRAMEBUFFER,GL_PIXEL_PACK_BUFFER,GL_FRAMEBUFFER_COMPLETE,GL_RGBA,GL_UNSIGNED_BYTE};
static int state[8]={0,42,99,7,8,9,10,11};static int reads=0;static bool complete=true;
static void glGetIntegerv(unsigned k,int *v){*v=state[k];}
static void glBindFramebuffer(unsigned,unsigned v){state[1]=v;}
static void glReadBuffer(unsigned v){state[2]=v;}
static void glBindBuffer(unsigned,unsigned v){state[3]=v;}
static void glPixelStorei(unsigned k,int v){state[k]=v;}
static unsigned glCheckFramebufferStatus(unsigned){return complete?GL_FRAMEBUFFER_COMPLETE:0;}
static void glReadPixels(int,int,int,int,unsigned,unsigned,void *p){++reads;auto b=(unsigned char*)p;b[0]=state[1]==5?13:0;b[1]=b[2]=0;b[3]=255;errno=99;}
'''+p['PROBE']+r'''
int main(){int old[8];for(int i=0;i<8;++i)old[i]=state[i];errno=17;
 if(probe031(5,12,2560,1600)!=9 || reads!=9 || errno!=17)return 1;
 for(int i=0;i<8;++i)if(old[i]!=state[i])return 2;
 if(probe031(0,12,2560,1600)!=0 || reads!=18)return 3;
 complete=false;if(probe031(5,12,2560,1600)!=-1 || reads!=18)return 4;
 for(int i=0;i<8;++i)if(old[i]!=state[i])return 5;
 if(probe031(5,12,0,1600)!=-1 || reads!=18)return 6;
 return 0;}
'''
remote='import tempfile,pathlib,subprocess\ncode='+repr(code)+'''
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=60)
assert 'glGetError' not in p['PROBE']
source='prefix\n'+p['COPY']+'\nsuffix'
new=p['instrument_copy'](source)
assert new.count('glBlitFramebuffer(')==source.count('glBlitFramebuffer(')==1
assert new.split('static bool copy_frame_gpu_025')[1].split('GLint saved_read=')[0]==source.split('static bool copy_frame_gpu_025')[1].split('GLint saved_read=')[0]
print('PASS: actual native probe preserves GL read/pack state and errno; bounded RGB observation only')

"""Compile the read-only dispatch observation against explicit GL query fixtures."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
assert (b/'commercial-gl-dispatch-033.py').exists(),'missing public GL dispatch observation'
p=runpy.run_path(str(b/'commercial-gl-dispatch-033.py'))
code=r'''
#include <cerrno>
#include <cassert>
using GLenum=unsigned;using GLint=int;using GLubyte=unsigned char;
enum {GL_VERSION=1,GL_RENDERER,GL_READ_FRAMEBUFFER_BINDING,GL_DRAW_FRAMEBUFFER_BINDING,GL_CURRENT_PROGRAM,GL_VIEWPORT};
static int queries=0;
static const GLubyte *getString(GLenum name){++queries;errno=99;return reinterpret_cast<const GLubyte *>(name==GL_VERSION?"OpenGL ES 3.2 fixture":"fixture only");}
static void getInteger(GLenum name,GLint *v){++queries;errno=99;if(name==GL_VIEWPORT){v[0]=1;v[1]=2;v[2]=2560;v[3]=1600;}else *v=int(name+10);}
'''+p['QUERY']+r'''
int main(){
 errno=17;auto a=query033(getString,getInteger);
 assert(errno==17 && queries==6 && a.version && a.renderer);
 assert(a.read_fbo==13 && a.draw_fbo==14 && a.program==15);
 assert(a.viewport[0]==1 && a.viewport[1]==2 && a.viewport[2]==2560 && a.viewport[3]==1600);
 auto empty=query033(nullptr,nullptr);assert(errno==17 && queries==6);
 assert(!empty.version && !empty.renderer && empty.read_fbo==-1 && empty.viewport[2]==-1);
}
'''
remote='import pathlib,tempfile,subprocess\ncode='+repr(code)+'''
with tempfile.TemporaryDirectory(prefix='gl-dispatch033-') as d:
 p=pathlib.Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=60)
assert 'RTLD_NOLOAD' in p['OBSERVE'] and 'dladdr(' in p['OBSERVE']
for forbidden in ['glGetError','eglGetError','glBind','glClear','glDraw','SetGlHookTable']:
  assert forbidden not in p['QUERY']+p['OBSERVE'],forbidden
remote=r'''
from pathlib import Path
import runpy
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
p=runpy.run_path(str(base/'commercial-gl-dispatch-033.py'))
source=Path('/home/zoinve/harmony-virgl-883/commercial-graphics-014/egl-commercial-014.cpp').read_text()
old=p['previous']['instrument'](source)
new=p['instrument'](source)
assert new.replace(p['QUERY']+p['OBSERVE']+'\n','',1).replace('\n    observe_dispatch033();','',1)==old
assert new.count('observe_dispatch033();')==1
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=30)
print('PASS: read-only public queries, null availability, state fields and errno; not target rendering proof')

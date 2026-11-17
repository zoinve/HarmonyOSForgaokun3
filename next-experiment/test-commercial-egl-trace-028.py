"""Forwarded EGL results must be observed, never replaced or called twice."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-egl-trace-028.py').exists(),'missing post-display boundary tracing'
p=runpy.run_path(str(base/'commercial-egl-trace-028.py'))
fixture=p['OLD_FORWARD']+'\n'+''.join(p['ENTRIES'])
source=p['instrument_forward'](fixture)
program='#include <cerrno>\n#include <cstring>\n#include <cstdint>\n#include <cstdarg>\n#include <dlfcn.h>\n'+p['HEADER']+r'''
static unsigned entered=0,exited=0,invoked=0;
static bool available=true;
extern "C" int HiLogPrint(int,int,unsigned,const char*,const char *format,...) {
 va_list args;va_start(args,format);const char *stage=va_arg(args,const char*);
 long value=va_arg(args,long);va_end(args);
 if(!strcmp(stage,"eglInitialize-entry"))++entered;
 if(!strcmp(stage,"eglInitialize-exit")){++exited;if(value!=7 && value!=0)__builtin_abort();}
 errno=99;return 0;
}
using EGLBoolean=unsigned;using EGLDisplay=void*;using EGLint=int;
constexpr EGLBoolean EGL_FALSE=0;
extern "C" EGLBoolean eglInitialize(EGLDisplay,EGLint*,EGLint*);
static EGLBoolean actual(EGLDisplay,EGLint*,EGLint*){++invoked;errno=23;return 7;}
template<class T> T real(const char*){return available ? reinterpret_cast<T>(actual):nullptr;}
'''+source.split('extern "C" EGLSurface')[0]+r'''
FORWARD(EGLBoolean, eglInitialize, (EGLDisplay d,EGLint *a,EGLint *b),(d,a,b),EGL_FALSE)
int main(){
 errno=17;if(eglInitialize(nullptr,nullptr,nullptr)!=7 || errno!=23 || invoked!=1)return 1;
 available=false;errno=19;
 if(eglInitialize(nullptr,nullptr,nullptr)!=0 || errno!=19 || invoked!=1)return 2;
 if(entered!=2 || exited!=2)return 3;
 for(int n=0;n<1000;++n)trace028("mesa",1);
 errno=31;trace028("eglInitialize-entry",0);
 if(entered!=3 || errno!=31)return 4;
}
'''
script='program='+repr(program)+'\n'+r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='commercial-egl028-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(program)
 subprocess.run(['c++','-rdynamic',str(p/'test.cpp'),'-ldl','-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True,timeout=60)
assert 'eglGetError(' not in source and 'O_CREAT' not in source
print('PASS: real forwarding result/fallback/single call/errno retained; lookup flood cannot suppress initialization')

"""Observe every own EGL return while retaining single invocation and errno."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-egl-trace-029.py').exists(),'missing own EGL return diagnostics'
p=runpy.run_path(str(base/'commercial-egl-trace-029.py'))
old=runpy.run_path(str(base/'commercial-egl-trace-028.py'))
fixture='\n'.join(entry+'\n    ++invoked; errno=23; return answer;\n}' for entry in old['ENTRIES'])
source=p['instrument_returns'](fixture)
program='#include <cerrno>\n#include <cstring>\n#include <cstdint>\n#include <cstdarg>\n#include <dlfcn.h>\n'+p['HEADER']+r'''
using EGLBoolean=uintptr_t;using EGLSurface=uintptr_t;using EGLDisplay=void*;
using EGLConfig=void*;using EGLNativeWindowType=void*;using EGLint=int;using EGLContext=void*;
static unsigned invoked=0,exited=0;static uintptr_t answer=0;
extern "C" int HiLogPrint(int,int,unsigned,const char*,const char *format,...){
 va_list args;va_start(args,format);const char *stage=va_arg(args,const char*);
 long value=va_arg(args,long);va_end(args);
 if(strstr(stage,"-exit")){++exited;if((uintptr_t)value!=answer)__builtin_abort();}
 errno=99;return 0;
}
'''+source+r'''
int main(){
 for(uintptr_t value: {uintptr_t(0),uintptr_t(7)}){
  answer=value;errno=17;
  if(eglMakeCurrent(nullptr,0,0,nullptr)!=answer || errno!=23)return 1;
  if(eglCreateWindowSurface(nullptr,nullptr,nullptr,nullptr)!=answer || errno!=23)return 2;
  if(eglSwapBuffers(nullptr,0)!=answer || errno!=23)return 3;
 }
 if(invoked!=6 || exited!=6)return 4;
}
'''
program='#include <initializer_list>\n'+program
script='program='+repr(program)+'\n'+r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='commercial-egl029-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(program)
 subprocess.run(['c++','-rdynamic',str(p/'test.cpp'),'-ldl','-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True,timeout=60)
assert 'eglGetError(' not in source and 'O_CREAT' not in source
print('PASS: three real return paths retain success/failure, single invocation and errno')

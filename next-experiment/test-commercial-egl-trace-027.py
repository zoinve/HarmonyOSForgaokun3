"""A noisy lookup phase must not hide later actual EGL boundaries."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-egl-trace-027.py').exists(),'missing independent stage quotas'
p=runpy.run_path(str(base/'commercial-egl-trace-027.py'))
program='#include <cerrno>\n#include <cstring>\n#include <dlfcn.h>\n'+p['HEADER']+r'''
static unsigned counts[6]={};
extern "C" int HiLogPrint(int type,int level,unsigned domain,const char*,const char *format,...) {
 if(type!=3 || level!=4 || domain!=0x0D002510)return -1;
 va_list args;va_start(args,format);const char *stage=va_arg(args,const char*);va_end(args);
 const char *stages[]={"mesa","platform-entry","platform-symbol","drm-open","gbm-device","mesa-display"};
 for(unsigned i=0;i<6;++i)if(!strcmp(stage,stages[i]))++counts[i];
 errno=99;return 0;
}
int main(){
 const char *stages[]={"mesa","platform-entry","platform-symbol","drm-open","gbm-device","mesa-display"};
 for(unsigned s=0;s<6;++s)for(unsigned n=0;n<1000;++n){errno=17;trace027(stages[s],n);if(errno!=17)return 1;}
 for(unsigned s=0;s<6;++s)if(counts[s]!=8)return 2;
 trace027("unknown",0);
 for(unsigned s=0;s<6;++s)if(counts[s]!=8)return 3;
}
'''
program='#include <cstdarg>\n'+program
script='program='+repr(program)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='commercial-egl-trace027-') as folder:
 p=Path(folder);(p/'test.cpp').write_text(program)
 subprocess.run(['c++','-rdynamic',str(p/'test.cpp'),'-ldl','-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True,timeout=60)
assert 'eglGetError(' not in p['HEADER'] and '0x0D002510' in p['HEADER']
print('PASS: 1000 lookups cannot suppress later stages; 8 logs per stage, 48 total; errno retained')

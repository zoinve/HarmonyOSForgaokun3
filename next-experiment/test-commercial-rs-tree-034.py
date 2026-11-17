"""Exercise the exact observation helper; never treat a dump request as desktop proof."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
assert (b/'commercial-rs-tree-034.py').exists(),'missing bounded original RS tree observation'
p=runpy.run_path(str(b/'commercial-rs-tree-034.py'))
code=r'''
#include <cstdio>
#include <cstring>
#include <cassert>
static int commercial_diag_fd003=1,calls=0;
static void commercial_command002(char *const args[]){
 assert(!strcmp(args[0],"/system/bin/hidumper"));
 assert(!strcmp(args[1],"-s") && !strcmp(args[2],"10") && !strcmp(args[3],"-a"));
 assert(!strcmp(args[4],calls==0?"screen":"MultiRSTrees") && args[5]==nullptr);
 ++calls;
}
'''+p['HELPER']+r'''
int main(){for(unsigned i=0;i<48;++i)commercial_rs_tree034(i);assert(calls==2);}
'''
remote='import tempfile,subprocess\nfrom pathlib import Path\ncode='+repr(code)+'''
with tempfile.TemporaryDirectory(prefix='rs-tree-034-') as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True,timeout=30)
old=runpy.run_path(str(b/'build-commercial-native-033.py'))['inner']
new=p['instrument'](old)
assert new.replace(p['HELPER'],'',1).replace('        commercial_rs_tree034(sample);\n','',1)==old
try:p['instrument'](new)
except AssertionError:pass
else:raise AssertionError('duplicate observation accepted')
print('PASS: two exact original RS query requests at one sample; inherited 3-second command bounds and all other bootstrap bytes unchanged')

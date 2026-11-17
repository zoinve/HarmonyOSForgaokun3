"""Real pixel statistics and bounded capture instrumentation, not desktop proof."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'commercial-frame-evidence-030.py').exists(), 'missing fresh source/output evidence'
p=runpy.run_path(str(base/'commercial-frame-evidence-030.py'))
code=r'''
#include <cstdint>
#include <cstddef>
#include <cassert>
'''+p['STATS']+r'''
int main(){
 unsigned char data[32]={};
 for(unsigned i=3;i<32;i+=4)data[i]=255;
 auto black=sample030(data,sizeof(data),2,2,16);
 assert(black.valid && black.nonblack==0 && black.samples==160*256);
 data[16]=17;
 auto color=sample030(data,sizeof(data),2,2,16);
 assert(color.valid && color.nonblack==80*128 && color.hash!=black.hash);
 assert(!sample030(data,19,2,2,16).valid);
 assert(!sample030(data,sizeof(data),3,2,8).valid);
 assert(!sample030(nullptr,sizeof(data),2,2,16).valid);
}
'''
remote="import subprocess,tempfile\nfrom pathlib import Path\ncode="+repr(code)+"\nwith tempfile.TemporaryDirectory(prefix='commercial-frame-030-') as d:\n p=Path(d);(p/'test.cpp').write_text(code);subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True);subprocess.run([str(p/'test')],check=True)\n"
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True)
remote=r'''
from pathlib import Path
import runpy
original=Path('/home/zoinve/harmony-virgl-883/commercial-graphics-014/composer-trace.cpp').read_text()
repair=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/commercial-frame-evidence-030.py')['instrument']
new=repair(original)
assert original[original.index('int copy_client(Scanout &output)'):]==new[new.index('int copy_client(Scanout &output)'):]
prefix=original[:original.index('static void native_capture_012')]
assert new.startswith(prefix)
assert 'sequence>=128' in new and 'now030-last030<1000000' in new
assert 'COMMERCIAL030_FRAME' in new and 'source_status030' in new
try:repair(new)
except AssertionError:pass
else:raise AssertionError('duplicate instrumentation accepted')
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True)
print('PASS: actual RGB samples ignore alpha, respect stride/bounds and detect nonblack input')

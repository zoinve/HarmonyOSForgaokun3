"""The cached transfer must be byte-identical to the tested landscape mapping."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-cached-copy-024.h').exists(),'missing cached DMA copy implementation'
payload=r'''
from pathlib import Path
import tempfile,subprocess
header=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
test=r"""
#include <cassert>
#include <cstring>
#include "native-cached-copy-024.h"
int main(){
 std::vector<unsigned char> cache_in,cache_out;
 for(unsigned w:{1,2,17,64})for(unsigned h:{1,3,19,47})for(bool rgba:{false,true}){
  unsigned stride=(h+3)*4,pitch=w*4+12;
  std::vector<unsigned char> src(stride*(w+2)),expected(pitch*h,0xac),actual(expected);
  for(size_t i=0;i<src.size();++i)src[i]=(i*91+7)%251;
  landscape_copy_023(expected.data(),pitch,w,h,src.data(),stride,1,1,h,w,rgba);
  cached_landscape_copy_024(actual.data(),pitch,w,h,src.data(),stride,1,1,h,w,rgba,cache_in,cache_out);
  assert(expected==actual); // Includes untouched destination row padding.
 }
}
"""
with tempfile.TemporaryDirectory(prefix='cached-copy-024-') as name:
 d=Path(name);(d/'test.cpp').write_text(test)
 subprocess.run(['g++','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(header),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True)
print('PASS cached transfer pixels, formats, padding, crops and reused buffers under sanitizers')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

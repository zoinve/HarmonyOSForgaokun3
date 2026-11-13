"""Real pixel mapping tests: rotation, formats, padding, crop and scaling."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-landscape-copy-023.h').exists(),'missing actual landscape rotation'
payload=r'''
from pathlib import Path
import subprocess,tempfile
header=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-landscape-copy-023.h')
test=r"""
#include <cassert>
#include <cstring>
#include "native-landscape-copy-023.h"
int main(){
 unsigned char src[80]={},out[100];
 for(unsigned y=0;y<4;y++)for(unsigned x=0;x<4;x++){
  auto p=src+y*20+x*4;p[0]=10*y+x;p[1]=77;p[2]=200;p[3]=12;
 }
 for(bool rgba:{false,true}){
  memset(out,0xaa,sizeof(out));
  landscape_copy_023(out,12,2,3,src,20,1,1,3,2,rgba);
  for(unsigned y=0;y<3;y++)for(unsigned x=0;x<2;x++){
   auto s=src+(2-x)*20+(1+y)*4;auto d=out+y*12+x*4;
   assert(d[0]==s[rgba?2:0] && d[1]==77 && d[2]==s[rgba?0:2] && d[3]==255);
  }
  assert(out[8]==0xaa && out[9]==0xaa && out[32]==0xaa);
  memset(out,0xaa,sizeof(out));
  landscape_copy_023(out,12,2,2,src,20,0,0,4,4,rgba);
  for(unsigned y=0;y<2;y++)for(unsigned x=0;x<2;x++){
   auto s=src+(1-x)*2*20+y*2*4;auto d=out+y*12+x*4;
   assert(d[0]==s[rgba?2:0] && d[2]==s[rgba?0:2]);
  }
 }
}
"""
with tempfile.TemporaryDirectory(prefix='landscape-copy-023-') as name:
 d=Path(name);(d/'test.cpp').write_text(test)
 subprocess.run(['g++','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(header.parent),str(d/'test.cpp'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True)
print('PASS real rotated pixels, both formats, padding, crop, scaling and sanitizers')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

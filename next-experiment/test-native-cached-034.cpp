#include "native-cached-copy-034.h"
#include <cassert>
#include <cstdio>
int main(){
 for(unsigned pw:{3u,16u,33u})for(unsigned ph:{7u,16u,20u})
 for(unsigned crop:{0u,2u})for(unsigned scale:{1u,2u})for(bool rgba:{false,true}){
  unsigned cw=ph*scale,ch=pw*scale,stride=(crop+cw+3)*4,pitch=pw*4+16;
  std::vector<unsigned char> src(size_t(stride)*(crop+ch));
  for(size_t n=0;n<src.size();++n)src[n]=(n*71+(n>>8))&255;
  std::vector<unsigned char> old(size_t(pitch)*ph,0xa7),now=old,in1,out1,in2,out2;
  cached_landscape_copy_024(old.data(),pitch,pw,ph,src.data(),stride,crop,crop,cw,ch,rgba,in1,out1);
  cached_landscape_copy_034(now.data(),pitch,pw,ph,src.data(),stride,crop,crop,cw,ch,rgba,in2,out2);
  assert(old==now);
  if(scale==1)assert(out2.empty());
 }
 std::puts("PASS 72 cached rotation/crop/scale/color combinations; intermediate copy absent for 1:1");
}

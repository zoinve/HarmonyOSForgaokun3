/* Exact-size landscape frames avoid scalar rotation and an intermediate copy.
 * Scaling/crop semantics and the existing DMA ownership remain unchanged. */
#pragma once
#include "native-cached-copy-024.h"
#include "native-rotation-034.h"
static inline void cached_landscape_copy_034(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,
 const unsigned char *src,unsigned stride,unsigned cx,unsigned cy,unsigned cw,unsigned ch,bool rgba,
 std::vector<unsigned char> &input,std::vector<unsigned char> &output)
{
 if(cw==ph&&ch==pw){
  input.resize(size_t(stride)*(cy+ch));
  std::memcpy(input.data(),src,input.size());
  if(rotate_1to1_034(dst,pitch,pw,ph,input.data()+size_t(cy)*stride+size_t(cx)*4,stride,rgba))return;
 }
 cached_landscape_copy_024(dst,pitch,pw,ph,src,stride,cx,cy,cw,ch,rgba,input,output);
}

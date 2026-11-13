/* Measured boundaries of 034; ownership, geometry and pixel algorithm unchanged. */
#pragma once
#include "native-cached-copy-024.h"
#include "native-rotation-034.h"
static inline void cached_landscape_copy_035(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,
 const unsigned char *src,unsigned stride,unsigned cx,unsigned cy,unsigned cw,unsigned ch,bool rgba,
 std::vector<unsigned char> &input,std::vector<unsigned char> &output)
{
 if(cw==ph&&ch==pw){
  auto read_start035=perf_now_023();
  input.resize(size_t(stride)*(cy+ch));
  std::memcpy(input.data(),src,input.size());
  perf_record_023("composer_dma_to_ram035",read_start035);
  auto rotate_start035=perf_now_023();
  bool rotated035=rotate_1to1_034(dst,pitch,pw,ph,input.data()+size_t(cy)*stride+size_t(cx)*4,stride,rgba);
  perf_record_023("composer_neon_rotate035",rotate_start035);
  if(rotated035)return;
 }
 cached_landscape_copy_024(dst,pitch,pw,ph,src,stride,cx,cy,cw,ch,rgba,input,output);
}

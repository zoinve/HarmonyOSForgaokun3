/* Exact clockwise 1:1 rotation. No DMA ownership or display timing changes. */
#pragma once
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#if defined(__aarch64__)
#include <arm_neon.h>
static inline uint32x4_t rotation_colors_034(uint32x4_t v,bool rgba){
 if(rgba)v=vorrq_u32(vandq_u32(v,vdupq_n_u32(0xff00ff00u)),
  vorrq_u32(vshrq_n_u32(vandq_u32(v,vdupq_n_u32(0x00ff0000u)),16),
            vshlq_n_u32(vandq_u32(v,vdupq_n_u32(0x000000ffu)),16)));
 v=vorrq_u32(v,vdupq_n_u32(0xff000000u));
 v=vrev64q_u32(v);
 return vextq_u32(v,v,2);
}
#endif
static inline bool rotate_1to1_034(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,
 const unsigned char *src,unsigned stride,bool rgba){
 if(!dst||!src||!pw||!ph||pw>16384||ph>16384||pitch<pw*4||stride<ph*4)return false;
 unsigned bw=ph&~3u,bh=pw&~3u;
#if defined(__aarch64__)
 for(unsigned ty=0;ty<bh;ty+=32)for(unsigned tx=0;tx<bw;tx+=32)
 for(unsigned sy=ty;sy<bh&&sy<ty+32;sy+=4)for(unsigned sx=tx;sx<bw&&sx<tx+32;sx+=4){
  uint32x4_t a=vreinterpretq_u32_u8(vld1q_u8(src+(size_t)sy*stride+sx*4));
  uint32x4_t b=vreinterpretq_u32_u8(vld1q_u8(src+(size_t)(sy+1)*stride+sx*4));
  uint32x4_t c=vreinterpretq_u32_u8(vld1q_u8(src+(size_t)(sy+2)*stride+sx*4));
  uint32x4_t d=vreinterpretq_u32_u8(vld1q_u8(src+(size_t)(sy+3)*stride+sx*4));
  uint32x4x2_t ab=vtrnq_u32(a,b),cd=vtrnq_u32(c,d);
  uint32x4_t out[4]={
   vcombine_u32(vget_low_u32(ab.val[0]),vget_low_u32(cd.val[0])),
   vcombine_u32(vget_low_u32(ab.val[1]),vget_low_u32(cd.val[1])),
   vcombine_u32(vget_high_u32(ab.val[0]),vget_high_u32(cd.val[0])),
   vcombine_u32(vget_high_u32(ab.val[1]),vget_high_u32(cd.val[1]))};
  for(unsigned k=0;k<4;++k)vst1q_u8(dst+(size_t)(sx+k)*pitch+(pw-sy-4)*4,
    vreinterpretq_u8_u32(rotation_colors_034(out[k],rgba)));
 }
#else
 bw=bh=0;
#endif
 for(unsigned sy=0;sy<pw;++sy)for(unsigned sx=(sy<bh?bw:0);sx<ph;++sx){
  const unsigned char *p=src+(size_t)sy*stride+sx*4;
  unsigned char *q=dst+(size_t)sx*pitch+(pw-1-sy)*4;
  q[0]=p[rgba?2:0];q[1]=p[1];q[2]=p[rgba?0:2];q[3]=255;
 }
 return true;
}

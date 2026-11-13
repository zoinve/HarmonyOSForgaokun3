/* Real pixel equivalence for the 1:1 rotation fast path, including stride guards. */
#include "native-rotation-034.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static double now034(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
/* Same 16x16 tiled loop and row table as the actual 023 production helper. */
static void reference034(unsigned char *dst,unsigned pitch,unsigned pw,unsigned ph,const unsigned char *src,unsigned stride,bool rgba){
 size_t *rows=malloc((size_t)pw*sizeof(*rows));assert(rows);
 for(unsigned x=0;x<pw;++x)rows[x]=(size_t)(pw-1-x)*stride;
 for(unsigned by=0;by<ph;by+=16)for(unsigned bx=0;bx<pw;bx+=16)
 for(unsigned y=by;y<ph&&y<by+16;++y)for(unsigned x=bx;x<pw&&x<bx+16;++x){
  const unsigned char *p=src+rows[x]+y*4;
  unsigned char *q=dst+(size_t)y*pitch+x*4;
  q[0]=p[rgba?2:0];q[1]=p[1];q[2]=p[rgba?0:2];q[3]=255;
 }
 free(rows);
}
int main(int argc,char **argv){
 (void)argv;
 const unsigned dims[][2]={{1,1},{3,7},{4,4},{8,12},{17,33},{1600,2560}};
 double old_ms=0,new_ms=0;
 for(unsigned i=0;i<sizeof(dims)/sizeof(dims[0]);++i){
  unsigned pw=dims[i][0],ph=dims[i][1],pitch=pw*4+16,stride=ph*4+32;
  size_t in_size=(size_t)stride*pw,out_size=(size_t)pitch*ph;
  unsigned char *src=malloc(in_size),*expected=malloc(out_size),*actual=malloc(out_size);
  assert(src&&expected&&actual);
  for(size_t n=0;n<in_size;++n)src[n]=(unsigned char)(n*17+(n>>8));
  for(unsigned rgba=0;rgba<2;++rgba){
   memset(expected,0xa7,out_size);memset(actual,0xa7,out_size);
   reference034(expected,pitch,pw,ph,src,stride,rgba);
   assert(rotate_1to1_034(actual,pitch,pw,ph,src,stride,rgba));
   assert(memcmp(expected,actual,out_size)==0);
  }
  if(argc>1 && i==5){
   unsigned count=24;
   double start=now034();for(unsigned n=0;n<count;++n)reference034(expected,pitch,pw,ph,src,stride,true);old_ms=(now034()-start)*1000/count;
   start=now034();for(unsigned n=0;n<count;++n)assert(rotate_1to1_034(actual,pitch,pw,ph,src,stride,true));new_ms=(now034()-start)*1000/count;
   assert(memcmp(expected,actual,out_size)==0);
  }
  free(src);free(expected);free(actual);
 }
 unsigned char guard[64];memset(guard,0x5a,sizeof(guard));
 assert(!rotate_1to1_034(guard,3,2,2,guard,8,false));
 for(unsigned n=0;n<sizeof(guard);++n)assert(guard[n]==0x5a);
 printf("{\"pixel_equivalence\":true,\"neon\":%s,\"reference_ms\":%.3f,\"fast_ms\":%.3f}\n",
#if defined(__aarch64__)
 "true",
#else
 "false",
#endif
 old_ms,new_ms);
 return 0;
}

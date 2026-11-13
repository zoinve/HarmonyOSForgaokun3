/* Supplementary real-GPU crop/scale/format contract, no KMS or service changes. */
#include "native-gpu-composer-041.h"
#include <cassert>
using namespace NativeGpu041;
static void sync_buffer(Buffer &b,uint64_t flags){dma_buf_sync s{flags};assert(!ioctl(b.fd,DMA_BUF_IOCTL_SYNC,&s));}
int main()
{
 assert(initialize(""));unsigned tests=0;
 for(unsigned format:{DRM_FORMAT_ABGR8888,DRM_FORMAT_XBGR8888,DRM_FORMAT_ARGB8888,DRM_FORMAT_XRGB8888}){
  Buffer src;assert(allocate(src,97,71,format));
  bool rgba=format==DRM_FORMAT_ABGR8888||format==DRM_FORMAT_XBGR8888;
  sync_buffer(src,DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
  for(unsigned y=0;y<src.height;++y)for(unsigned x=0;x<src.width;++x){
   auto p=static_cast<unsigned char*>(src.map)+y*src.pitch+x*4;
   p[rgba?0:2]=(x*13+y*3)&255;p[1]=(x+y*17)&255;p[rgba?2:0]=(x*7+y*11)&255;p[3]=37;
  }
  sync_buffer(src,DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);
  for(unsigned pw:{31u,67u})for(unsigned ph:{43u,83u})for(unsigned cw:{65u,80u}){
   Buffer out;assert(allocate(out,pw,ph,DRM_FORMAT_XRGB8888));
   const int cx=3,cy=5,ch=50;CursorSnapshot032 c{0,int(ph)-1,int(pw)-1,true};
   assert(frame(out,src.fd,src.width,src.height,src.pitch,format,cx,cy,cw,ch,c));
   assert(!frame(out,src.fd,src.width,src.height,src.pitch,format,90,cy,cw,ch,c));
   assert(repaint(out,c));
   std::vector<unsigned char> bg(out.pitch*out.height,0),expected(bg.size());
   for(unsigned y=0;y<out.height;++y)for(unsigned x=0;x<out.width;++x){
    unsigned lx=cx+uint64_t(y)*cw/ph,ly=cy+uint64_t(pw-1-x)*ch/pw;
    auto p=bg.data()+y*out.pitch+x*4;
    p[0]=(lx*7+ly*11)&255;p[1]=(lx+ly*17)&255;p[2]=(lx*13+ly*3)&255;p[3]=255;
   }
   assert(cursor_frame_032(expected.data(),expected.size(),out.pitch,pw,ph,bg,c));
   sync_buffer(out,DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);
   for(unsigned y=0;y<ph;++y)for(unsigned x=0;x<pw;++x)
    assert(!memcmp(static_cast<unsigned char*>(out.map)+y*out.pitch+x*4,expected.data()+y*out.pitch+x*4,3));
   sync_buffer(out,DMA_BUF_SYNC_END|DMA_BUF_SYNC_READ);release(out);++tests;
  }
  release(src);
 }
 shutdown();assert(tests==32);puts("PASS: real GPU 32 RGBA/RGBX/BGRA/BGRX crop/scale/edge-cursor cases; invalid crops rejected; no modeset");
}

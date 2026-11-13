/* Real GPU contract test, no modeset. Input release and context migration matter. */
#include "native-gpu-composer-041.h"
#include <cassert>
#include <thread>
#include <utility>
using namespace NativeGpu041;
static void sync_buffer(Buffer &b,uint64_t flags){dma_buf_sync s{flags};assert(!ioctl(b.fd,DMA_BUF_IOCTL_SYNC,&s));}
static void check(Buffer &out,CursorSnapshot032 c)
{
 sync_buffer(out,DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ);
 std::vector<unsigned char> bg(out.pitch*out.height,0),expected(bg.size());
 for(unsigned y=0;y<out.height;++y)for(unsigned x=0;x<out.width;++x){
  unsigned lx=y,ly=out.width-1-x;auto p=bg.data()+y*out.pitch+x*4;
  p[0]=(lx*7+ly*11)&255;p[1]=(lx+ly*17)&255;p[2]=(lx*13+ly*3)&255;p[3]=255;
 }
 assert(cursor_frame_032(expected.data(),expected.size(),out.pitch,out.width,out.height,bg,c));
 for(unsigned y=0;y<out.height;++y)for(unsigned x=0;x<out.width;++x)
  assert(!memcmp(static_cast<unsigned char*>(out.map)+y*out.pitch+x*4,expected.data()+y*out.pitch+x*4,3));
 sync_buffer(out,DMA_BUF_SYNC_END|DMA_BUF_SYNC_READ);
}
int main()
{
 assert(initialize(""));
 for(auto size: {std::pair<unsigned,unsigned>{64,80},{1600,2560}}){
  Buffer src,out;assert(allocate(src,size.second,size.first,DRM_FORMAT_ABGR8888));
  assert(allocate(out,size.first,size.second,DRM_FORMAT_XRGB8888));
  sync_buffer(src,DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE);
  for(unsigned y=0;y<src.height;++y)for(unsigned x=0;x<src.width;++x){auto p=static_cast<unsigned char*>(src.map)+y*src.pitch+x*4;
   p[0]=(x*13+y*3)&255;p[1]=(x+y*17)&255;p[2]=(x*7+y*11)&255;p[3]=255;}
  sync_buffer(src,DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE);
  CursorSnapshot032 c{0,17,19,true};
  assert(frame(out,src.fd,src.width,src.height,src.pitch,DRM_FORMAT_ABGR8888,0,0,src.width,src.height,c));check(out,c);
  release(src); // Idle repaint must not touch this now-closed input.
  for(auto point: {std::pair<int,int>{0,0},{int(size.second)-1,0},{0,int(size.first)-1},{int(size.second)-1,int(size.first)-1}}){
   c.x=point.first;c.y=point.second;
   std::thread worker([&]{assert(repaint(out,c));});worker.join();check(out,c);
  }
  c.visible=false;assert(repaint(out,c));check(out,c);
  invalidate();assert(!repaint(out,c));release(out);
 }
 shutdown();puts("PASS: real GPU RGB, corners, hide, released-input idle repaint and context migration; no modeset");
}

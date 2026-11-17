"""Observe completed client/scanout maps once; never change composition."""
HELPER = r'''
#include <sys/stat.h>
#include "native-full-capture-068.h"
static void full068_capture(const Scanout &buffer){
 const int saved068=errno;
 static bool attempted068=false;
 const uint64_t now068=perf_now_023();
 if(attempted068 || now068<120000000 || now068>=145000000){errno=saved068;return;}
 attempted068=true;
 bool good068=false,output_sync068=false,source_sync068=false;
 uint64_t source_bytes068=0,output_bytes068=0;
 int dir068=open("/data/native-full-068",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
 void *source068=MAP_FAILED;
 struct stat directory068={};
 dma_buf_sync sync068={DMA_BUF_SYNC_START|DMA_BUF_SYNC_READ};
 if(dir068>=0 && !fstat(dir068,&directory068) && directory068.st_uid==geteuid() &&
    (directory068.st_mode&0777)==0700 && valid(state.client) &&
    buffer.map!=MAP_FAILED && buffer.map){
  output_sync068=ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync068)==0;
  if(output_sync068)source_sync068=ioctl(state.client_fd,DMA_BUF_IOCTL_SYNC,&sync068)==0;
  if(source_sync068){
   source068=mmap(nullptr,state.client.size,PROT_READ,MAP_SHARED,state.client_fd,0);
   if(source068!=MAP_FAILED){
    Full068View source_view068={static_cast<const unsigned char *>(source068),uint64_t(state.client.size),
      unsigned(state.client.width),unsigned(state.client.height),unsigned(state.client.stride),
      state.client.format==PIXEL_FMT_RGBA_8888 || state.client.format==PIXEL_FMT_RGBX_8888};
    Full068View output_view068={static_cast<const unsigned char *>(buffer.map),buffer.size,
      unsigned(state.drm.mode.hdisplay),unsigned(state.drm.mode.vdisplay),buffer.pitch,false};
    good068=full068_write_ppm(dir068,"source.part",source_view068,&source_bytes068) &&
      full068_write_ppm(dir068,"output.part",output_view068,&output_bytes068);
    if(munmap(source068,state.client.size))good068=false;
   }
  }
 }
 sync068.flags=DMA_BUF_SYNC_END|DMA_BUF_SYNC_READ;
 if(source_sync068 && ioctl(state.client_fd,DMA_BUF_IOCTL_SYNC,&sync068))good068=false;
 if(output_sync068 && ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync068))good068=false;
 if(good068)good068=full068_publish(dir068,source_bytes068,output_bytes068,now068,buffer.fb);
 int error068=good068?0:errno;
 if(dir068>=0)close(dir068);
 int trace068=open("/data/native-perf-023.trace",O_WRONLY|O_APPEND|O_NOFOLLOW|O_CLOEXEC);
 if(trace068>=0){
  dprintf(trace068,"COMMERCIAL068_FULL_FRAME success=%d mono_us=%llu elapsed_us=%llu fb=%u source_bytes=%llu output_bytes=%llu source_w=%d source_h=%d source_stride=%d source_format=%d output_w=%u output_h=%u output_stride=%u errno=%d\n",
   int(good068),(unsigned long long)now068,(unsigned long long)(perf_now_023()-now068),buffer.fb,
   (unsigned long long)source_bytes068,(unsigned long long)output_bytes068,
   state.client.width,state.client.height,state.client.stride,state.client.format,
   unsigned(state.drm.mode.hdisplay),unsigned(state.drm.mode.vdisplay),buffer.pitch,error068);
  close(trace068);
 }
 errno=saved068;
}
'''


def instrument(source):
    assert 'COMMERCIAL068_FULL_FRAME' not in source
    anchor = 'static void native_capture_012(const Scanout &buffer)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, HELPER + '\n' + anchor, 1)
    anchor += '\n{\n'
    assert source.count(anchor) == 1
    return source.replace(anchor, anchor + '    full068_capture(buffer);\n', 1)

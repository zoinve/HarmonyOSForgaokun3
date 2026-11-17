"""Fresh, bounded observations of real client and completed scanout buffers."""
STATS=r'''
struct Sample030 { bool valid=false; unsigned samples=0,nonblack=0; uint64_t hash=1469598103934665603ULL; };
static Sample030 sample030(const void *map,uint64_t size,unsigned width,unsigned height,unsigned stride){
 Sample030 result;
 if(!map || !width || !height || uint64_t(stride)<uint64_t(width)*4 ||
    uint64_t(height-1)*stride+uint64_t(width)*4>size)return result;
 result.valid=true;
 for(unsigned y=0;y<256;++y)for(unsigned x=0;x<160;++x){
  const auto *pixel=static_cast<const unsigned char *>(map)+
   (uint64_t(y)*height/256)*stride+(uint64_t(x)*width/160)*4;
  ++result.samples;if(pixel[0]||pixel[1]||pixel[2])++result.nonblack;
  for(unsigned c=0;c<3;++c){result.hash^=pixel[c];result.hash*=1099511628211ULL;}
 }
 return result;
}
'''
OBSERVE=r'''
    Sample030 output030=sample030(buffer.map,buffer.size,state.drm.mode.hdisplay,state.drm.mode.vdisplay,buffer.pitch);
    Sample030 source030;int source_status030=-1;
    dma_buf_sync source_sync030={DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ};
    if(!ioctl(state.client_fd,DMA_BUF_IOCTL_SYNC,&source_sync030)){
        void *map030=mmap(nullptr,state.client.size,PROT_READ,MAP_SHARED,state.client_fd,0);
        if(map030!=MAP_FAILED){
            source030=sample030(map030,state.client.size,state.client.width,state.client.height,state.client.stride);
            munmap(map030,state.client.size);source_status030=source030.valid?0:-2;
        }
        source_sync030.flags=DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
        if(ioctl(state.client_fd,DMA_BUF_IOCTL_SYNC,&source_sync030))source_status030=-3;
    }
    int evidence030=open("/data/native-perf-023.trace",O_WRONLY|O_APPEND|O_CLOEXEC|O_NOFOLLOW);
    if(evidence030>=0){
        dprintf(evidence030,"COMMERCIAL030_FRAME sequence=%u mono_us=%llu fb=%u ppm_good=%d source_status=%d source_nonblack=%u source_samples=%u source_hash=%llu output_valid=%d output_nonblack=%u output_samples=%u output_hash=%llu client_w=%d client_h=%d client_stride=%d client_format=%d gpu_owned=%d\n",
          sequence,(unsigned long long)perf_now_023(),buffer.fb,int(good),source_status030,
          source030.nonblack,source030.samples,(unsigned long long)source030.hash,int(output030.valid),
          output030.nonblack,output030.samples,(unsigned long long)output030.hash,
          state.client.width,state.client.height,state.client.stride,state.client.format,int(buffer.gpu_owned));
        close(evidence030);
    }
'''

def instrument(source):
    anchor='static void native_capture_012(const Scanout &buffer)'
    assert source.count(anchor)==1
    assert 'COMMERCIAL030_FRAME' not in source
    source=source.replace(anchor,STATS+'\n'+anchor,1)
    old='if(++sequence>5 && sequence%30){errno=saved;return;}'
    assert source.count(old)==1
    source=source.replace(old,'''static uint64_t last030=0;
    uint64_t now030=perf_now_023();
    if(sequence>=128 || (sequence>=5 && now030-last030<1000000)){errno=saved;return;}
    ++sequence;last030=now030;''',1)
    anchor='    native_trace_007(good?"scanout_capture_success":"scanout_capture_failed",int(buffer.fb));'
    assert source.count(anchor)==1
    # Output CPU read sync has ended here; read the same mapping under a fresh sync.
    block='''    sync.flags=DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
    if(!ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync)){
'''+OBSERVE+'''        sync.flags=DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
        (void)ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync);
    }
'''
    return source.replace(anchor,block+anchor,1)

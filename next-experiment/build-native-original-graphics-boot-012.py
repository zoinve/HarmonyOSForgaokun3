"""Diagnostic-only real scanout capture and original account/application startup logs."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-011.py'))
inner=p['inner'].replace('COMPOSER_SRV,Composer,','AccountMgrService,OsAccountManager,BMS,BundleMgrService,AppSpawn,AbilityManagerService,COMPOSER_SRV,Composer,')
capture=r'''
static void native_capture_012(const Scanout &buffer)
{
    const int saved=errno; static unsigned sequence=0;
    if(++sequence>5 && sequence%30){errno=saved;return;}
    dma_buf_sync sync={DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ};
    if(ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync)){errno=saved;return;}
    int fd=open("/data/native-scanout-012.tmp",O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC,0644);
    bool good=fd>=0;
    if(good)good=dprintf(fd,"P6\n160 256\n255\n")>0;
    for(unsigned y=0;good && y<256;++y){
        unsigned char row[160*3];
        const auto src=static_cast<const unsigned char *>(buffer.map)+
            size_t(uint64_t(y)*state.drm.mode.vdisplay/256)*buffer.pitch;
        for(unsigned x=0;x<160;++x){
            auto pixel=src+(uint64_t(x)*state.drm.mode.hdisplay/160)*4;
            row[x*3]=pixel[2];row[x*3+1]=pixel[1];row[x*3+2]=pixel[0];
        }
        size_t done=0;while(done<sizeof(row)){
            ssize_t n=write(fd,row+done,sizeof(row)-done);
            if(n<0 && errno==EINTR)continue;
            if(n<=0){good=false;break;}done+=size_t(n);
        }
    }
    if(fd>=0 && close(fd))good=false;
    sync.flags=DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
    if(ioctl(buffer.dma_fd,DMA_BUF_IOCTL_SYNC,&sync))good=false;
    if(good)rename("/data/native-scanout-012.tmp","/data/native-scanout-012.ppm");
    errno=saved;
}
'''
dump=r'''
            if(sample==9 || sample==11){
                int pixels=open("/data/native-scanout-012.ppm",O_RDONLY|O_CLOEXEC);
                dprintf(1,"NATIVE_PIXELS012_BEGIN sample=%u fd=%d errno=%d\n",sample,pixels,errno);
                if(pixels>=0){
                    unsigned char bytes[128];ssize_t n;unsigned offset=0;
                    while(offset<130000 && (n=read(pixels,bytes,sizeof(bytes)))>0){
                        char line[257];for(ssize_t j=0;j<n;++j)snprintf(line+j*2,3,"%02x",bytes[j]);
                        dprintf(1,"NATIVE_PIXELS012_HEX %u %s\n",offset,line);offset+=(unsigned)n;
                    }close(pixels);dprintf(1,"NATIVE_PIXELS012_END bytes=%u\n",offset);
                }
            }
'''
anchor='        sleep(5);'
# Insert in the passive observer only, immediately before existing per-sample diagnostics.
anchor='        graphics_diagnostics_005(sample);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+'\n'+dump)
outer=p['outer'].replace('native-original-011-%s','native-original-012-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-011','native-original-graphics-boot-012')
anchor="src=work/'composer-trace.cpp';src.write_text(source)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,r'''
assert source.count('int copy_client(Scanout &output)')==1
source=source.replace('int copy_client(Scanout &output)',CAPTURE+'\nint copy_client(Scanout &output)')
assert source.count('state.front = slot; return OK;')==1
source=source.replace('state.front = slot; return OK;','state.front = slot; native_capture_012(state.buffers[slot]); return OK;')
assert source.count('return wait_flip(); // synchronous')==1
source=source.replace('return wait_flip(); // synchronous','int finished=wait_flip(); if(!finished)native_capture_012(state.buffers[slot]); return finished; // synchronous')
'''+anchor)
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

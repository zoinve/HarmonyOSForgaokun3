"""Independent original-service GPU composer; preserve 034 and real MMI adapter."""
import subprocess
payload=r"""
from pathlib import Path
import subprocess,hashlib,json,shutil
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
old=root/'native-render-034';work=root/'native-render-041';local=base.parent/'reports/native-render-041'
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((old/'result.json').read_text())
for n,h in r['sha256'].items():assert sha(old/n)==h
s=(old/'composer-trace.cpp').read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b,1)
replace('#include "native-cursor-state-032.h"','#include "native-cursor-state-032.h"\n#include "native-gpu-composer-041.h"')
replace('struct Scanout { int dma_fd', 'struct Scanout { NativeGpu041::Buffer gpu; bool gpu_owned=false; int dma_fd')
replace('    if (buffer.map != MAP_FAILED) munmap(buffer.map, buffer.size);', '''    if(buffer.gpu_owned){
        if(buffer.fb)drmModeRmFB(state.drm.fd,buffer.fb);
        if(buffer.gem){drm_gem_close close_gem={};close_gem.handle=buffer.gem;ioctl(state.drm.fd,DRM_IOCTL_GEM_CLOSE,&close_gem);}
        NativeGpu041::release(buffer.gpu);buffer=Scanout{};return;
    }
    if (buffer.map != MAP_FAILED) munmap(buffer.map, buffer.size);''')
replace('static void cursor_tick_032();', '''static bool gpu_scanouts_041()
{
    if(!NativeGpu041::initialize("/system/lib64/lab-freedreno003/"))return false;
    bool good=true;
    for(auto &b:state.buffers){
        b.gpu_owned=true;
        if(!NativeGpu041::allocate(b.gpu,state.drm.mode.hdisplay,state.drm.mode.vdisplay,DRM_FORMAT_XRGB8888)){good=false;break;}
        b.dma_fd=b.gpu.fd;b.pitch=b.gpu.pitch;b.size=b.gpu.size;b.map=b.gpu.map;
        if(drmPrimeFDToHandle(state.drm.fd,b.dma_fd,&b.gem)){good=false;break;}
        uint32_t handles[4]={b.gem},pitches[4]={b.pitch},offsets[4]={};
        if(drmModeAddFB2(state.drm.fd,b.gpu.width,b.gpu.height,DRM_FORMAT_XRGB8888,handles,pitches,offsets,&b.fb,0)){good=false;break;}
    }
    native_trace_007(good?"gpu_scanout_ready041":"gpu_scanout_fallback041",good);
    if(!good){for(auto &b:state.buffers)release(b);NativeGpu041::shutdown();}
    return good;
}
static void cursor_tick_032();''')
replace('    for (auto &buffer : state.buffers) {\n        drm_mode_create_dumb request', '    if(!gpu_scanouts_041())for (auto &buffer : state.buffers) {\n        drm_mode_create_dumb request')
replace('#include "native-cursor-composer-032.h"','#include "native-cursor-composer-041.h"')
anchor='    void *source = mmap(nullptr, client.size, PROT_READ, MAP_SHARED, state.client_fd, 0);'
replace(anchor,'''    if(output.gpu_owned){
        auto start041=perf_now_023();
        uint32_t format041=client.format==PIXEL_FMT_RGBA_8888?DRM_FORMAT_ABGR8888:
            client.format==PIXEL_FMT_RGBX_8888?DRM_FORMAT_XBGR8888:
            client.format==PIXEL_FMT_BGRA_8888?DRM_FORMAT_ARGB8888:DRM_FORMAT_XRGB8888;
        if(NativeGpu041::frame(output.gpu,state.client_fd,client.width,client.height,client.stride,format041,
                              crop.x,crop.y,crop.w,crop.h,cursor_snapshot_032())){
            state.cursor_background.clear();
            perf_record_023("composer_gpu_two_pass041",start041);return OK;
        }
        NativeGpu041::invalidate();perf_record_023("composer_gpu_cpu_fallback041",start041);
    }
'''+anchor)
# There are separate fail/destructor buffer-release loops. Shutdown only after all buffers.
anchor='    for (auto &buffer : buffers) release(buffer);'
replace(anchor,anchor+'\n    NativeGpu041::shutdown();')
(work/'composer-trace.cpp').write_text(s)
cursor=(base/'native-cursor-composer-032.h').read_text()
cursor=cursor.replace('if(state.front<0 || state.cursor_background.empty())continue;',
 'if(state.front<0 || (state.cursor_background.empty() && !NativeGpu041::background_valid))continue;',1)
a='''        dma_buf_sync sync={DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE};
        if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync))continue;
        bool painted=paint_cursor_032(output);
        sync.flags=DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE;
        if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync) || !painted)continue;'''
b='''        bool painted=false;
        if(output.gpu_owned && NativeGpu041::background_valid){
            painted=NativeGpu041::repaint(output.gpu,current);
        }else{
            dma_buf_sync sync={DMA_BUF_SYNC_START|DMA_BUF_SYNC_WRITE};
            if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync))continue;
            painted=paint_cursor_032(output);
            sync.flags=DMA_BUF_SYNC_END|DMA_BUF_SYNC_WRITE;
            if(ioctl(output.dma_fd,DMA_BUF_IOCTL_SYNC,&sync))painted=false;
        }
        if(!painted)continue;'''
assert cursor.count(a)==1;cursor=cursor.replace(a,b,1)
(work/'native-cursor-composer-041.h').write_text(cursor)
for n in ['libcursor_drawing_adapter.z.so','libcursor_drawing_adapter032.z.so']:shutil.copyfile(old/n,work/n)
cmd=[x.replace(str(old),str(work)) for x in r['commands'][0]]
cmd.extend(['-I'+str(work)])
with (local/'compile.stdout').open('xb') as out,(local/'compile.stderr').open('xb') as err:
 result=subprocess.run(cmd,stdout=out,stderr=err,timeout=120)
assert result.returncode==0,result.returncode
for n,h in r['sha256'].items():assert sha(old/n)==h
names=['composer-trace.cpp','libdisplay_composer_vdi_impl.z.so','libcursor_drawing_adapter.z.so','libcursor_drawing_adapter032.z.so']
data=dict(sha256={n:sha(work/n) for n in names},commands=[cmd],old034_unchanged=True,input_injection=False,
 acceleration='Actual FD690 shader rotation and cursor, GBM-owned scanouts; CPU NEON fallback',
 installed=False,runtime_verified=False,desktop_fps_verified=False)
for p in [work/'result.json',local/'result.json']:p.write_text(json.dumps(data,indent=2))
shutil.copyfile(work/'composer-trace.cpp',local/'composer-trace.cpp');shutil.copyfile(work/'native-cursor-composer-041.h',local/'native-cursor-composer-041.h')
print(json.dumps(data,indent=2))
"""
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

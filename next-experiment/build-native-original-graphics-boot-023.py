"""Actual logical landscape rotation plus bounded real GPU/frame-stage telemetry."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-022.py'))
inner=p['inner']
anchor='    pid_t observer = fork();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    int perf=open("/data/native-perf-023.trace",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0666);
    if(perf<0 || fchmod(perf,0666) || close(perf))fail("performance trace");
'''+anchor)
inner=inner.replace('        graphics_diagnostics_005(sample);','        graphics_diagnostics_005(sample);\n        diagnostic_file_002(sample,"/data/native-perf-023.trace");')
inner,n=re.subn(r'"-T","[^"]+"','"-T","Composer,RSScreenManager,RSScreenPreprocessor,RSMainThread,OHOS::RS,RenderService,DisplayManager,WindowManager,MMI,InputWindowsManager"',inner,count=1)
assert n==1
outer=p['outer'].replace('native-original-022-%s','native-original-023-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
prefix=payload[:offset];wrapper=prefix[prefix.index('WRAPPER=')+len('WRAPPER='):prefix.index('\nCAPTURE=')]
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+wrapper+'\nCAPTURE='+repr(p['capture'])+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-022','native-original-graphics-boot-023')
telemetry=r'''
#include <time.h>
static uint64_t perf_now_023(){timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return uint64_t(t.tv_sec)*1000000+t.tv_nsec/1000;}
static void perf_record_023(const char *stage,uint64_t start,const char *detail=""){
 int saved=errno;static unsigned calls=0;
 if(__atomic_add_fetch(&calls,1,__ATOMIC_RELAXED)<=128){
  auto end=perf_now_023();int fd=open("/data/native-perf-023.trace",O_WRONLY|O_APPEND|O_CLOEXEC);
  if(fd>=0){dprintf(fd,"NATIVE_PERF023 pid=%d uid=%d stage=%s mono_us=%llu elapsed_us=%llu %s\n",getpid(),getuid(),stage,(unsigned long long)end,(unsigned long long)(end-start),detail);close(fd);}
 }errno=saved;
}
struct PerfScope023{const char *name;uint64_t start;explicit PerfScope023(const char *s):name(s),start(perf_now_023()){}~PerfScope023(){perf_record_023(name,start);}};
'''
# Generate from pinned, unmodified reference, after existing diagnostic instrumentation.
adapt=r'''
header=project/'next-experiment/native-landscape-copy-023.h'
(work/header.name).write_bytes(header.read_bytes())
source=source.replace('using namespace AuroraComposer;',TELEMETRY+'\n#include "native-landscape-copy-023.h"\nusing namespace AuroraComposer;')
old='*out = {{state.drm.mode.hdisplay, state.drm.mode.vdisplay,'
assert source.count(old)==1
source=source.replace(old,'*out = {{state.drm.mode.vdisplay, state.drm.mode.hdisplay,')
old='out->phyWidth = state.drm.mm_width; out->phyHeight = state.drm.mm_height;'
assert source.count(old)==1
source=source.replace(old,'out->phyWidth = state.drm.mm_height; out->phyHeight = state.drm.mm_width;')
start=source.index('    for (uint32_t y = 0; y < state.drm.mode.vdisplay; ++y) {')
end=source.index('    if (trace) {',start)
source=source[:start]+r"""    landscape_copy_023(static_cast<unsigned char *>(output.map),output.pitch,
        state.drm.mode.hdisplay,state.drm.mode.vdisplay,static_cast<const unsigned char *>(source),
        client.stride,crop.x,crop.y,crop.w,crop.h,rgba);
    if(trace)for(uint32_t y=0;y<state.drm.mode.vdisplay;++y)for(uint32_t x=0;x<state.drm.mode.hdisplay;++x){
        auto pixel=static_cast<unsigned char *>(output.map)+size_t(y)*output.pitch+x*4;
        if(pixel[0]||pixel[1]||pixel[2])++nonblack;
    }
"""+source[end:]
for signature,stage in [('int copy_client(Scanout &output)','composer_copy_rotate'),('int wait_flip()','composer_wait_flip')]:
 old=signature+'\n{';assert source.count(old)==1
 source=source.replace(old,old+'\n    PerfScope023 timing("'+stage+'");')
source=source.replace('native_trace_007("GetDisplaySupportedModes",0);','native_trace_007("GetDisplaySupportedModes",0); perf_record_023("logical_mode",perf_now_023(),"logical=2560x1600 panel=1600x2560 rotation=CW");')
'''
anchor="src=work/'composer-trace.cpp';src.write_text(source)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,adapt+'\n'+anchor)
extra=r'''
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
tool=root/'window-bridge/toolchain';prefix=root/'prefix/system'
mesa=root/'native-original-graphics-bundle-001/bundle/system/lib64/lab-freedreno003'
egl_original=(ref/'egl_window_bridge.cpp').read_text()
egl=egl_original.replace('/system/lib64/aurora-mesa/libEGL.so.1','/system/lib64/lab-freedreno003/libEGL.so.1')
egl=egl.replace('namespace {',TELEMETRY+'\nnamespace {',1)
old='bool copy_frame(Window &window, BufferHandle &buffer)\n{';assert egl.count(old)==1
egl=egl.replace(old,old+'\n    PerfScope023 timing("egl_copy_frame");\n    uint64_t readback_start_023=perf_now_023();')
old='    glFinish();';assert egl.count(old)==1
egl=egl.replace(old,old+'\n    perf_record_023("egl_readback_finish",readback_start_023);')
old='    return fn(egl, backing(draw), backing(read), context);'
if old not in egl:
 # The pinned bridge has its actual successful MakeCurrent return here.
 old='    if (!fn(egl, backing(draw), backing(read), context)) return EGL_FALSE;'
 assert egl.count(old)==1
 egl=egl.replace(old,old+r"""
    static bool renderer_logged_023=false;
    if(context!=EGL_NO_CONTEXT && !renderer_logged_023){
        renderer_logged_023=true;char text[512];
        snprintf(text,sizeof(text),"renderer=%s vendor=%s version=%s",glGetString(GL_RENDERER),glGetString(GL_VENDOR),glGetString(GL_VERSION));
        perf_record_023("active_gl_context",perf_now_023(),text);
    }
""")
else:raise AssertionError('Review changed reference MakeCurrent before instrumentation')
egl_src=work/'egl-perf-023.cpp';egl_src.write_text(egl)
egl_out=work/'libEGL_impl.so'
includes=['-I'+str(ref),'-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
cmd=[str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES',*includes,str(egl_src),str(root/'native-original-graphics-bundle-001/drm_device.o'),str(mesa/'libGLESv2.so.2'),str(mesa/'libgbm.so.1'),str(mesa/'libdrm.so.2'),'-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-freedreno003','-o',str(egl_out)]
r=subprocess.run(cmd,capture_output=True,text=True)
(local/'egl-perf-compile.stdout').write_text(r.stdout);(local/'egl-perf-compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
target='native-target/graphics-egl/libEGL_impl.so';assert target in entries
entries[target]=(entries[target][0],egl_out.read_bytes())
assert (ref/'egl_window_bridge.cpp').read_text()==egl_original
with (local/'landscape-performance.json').open('x') as f:
 json.dump(dict(logical_width=2560,logical_height=1600,physical_panel_width=1600,physical_panel_height=2560,physical_timing_modified=False,rotation='clockwise real pixel rotation',rotation_source_sha256=sha(header),composer_source_sha256=sha(src),egl_source_sha256=sha(egl_src),egl_sha256=sha(egl_out),egl_command=cmd,gpu_hardware_acceleration_inferred_from_library_load=False),f,indent=2)
'''
anchor='def member(name,mode,data,ino):';assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor)
payload=payload.replace("changes='diagnostics only; original return values and credentials preserved'","changes='implemented landscape logical mode and real clockwise pixel rotation; performance diagnostics; credentials preserved'")
payload='TELEMETRY='+repr(telemetry)+'\n'+payload
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

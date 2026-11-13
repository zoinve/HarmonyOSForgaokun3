"""Bounded RAM-only composer entry/result diagnostics; no graphics behavior fix."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'build-native-original-graphics-boot-005.py'))
inner,outer=previous['inner'],previous['outer']
anchor='    pid_t observer = fork();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'''    int trace=open("/data/native-composer-006.trace",O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0666);
    if(trace<0 || fchmod(trace,0666))fail("composer trace create");
    close(trace);
'''+anchor)
inner=inner.replace('        graphics_diagnostics_005(sample);','        graphics_diagnostics_005(sample);\n        diagnostic_file_002(sample,"/data/native-composer-006.trace");')
outer=outer.replace('native-original-005-%s','native-original-006-%s')
instrument=r'''
import re
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
reference=ref/'composer.cpp';original=reference.read_text()
helper=r"""
static void native_trace_006(const char *name,int value)
{
    int saved=errno;static unsigned count=0;
    if(__atomic_add_fetch(&count,1,__ATOMIC_RELAXED)<=256){
        int fd=open("/data/native-composer-006.trace",O_WRONLY|O_APPEND|O_CLOEXEC);
        if(fd>=0){dprintf(fd,"NATIVE_COMPOSER006 pid=%d uid=%d call=%s value=%d errno=%d\n",getpid(),getuid(),name,value,saved);close(fd);}
    }errno=saved;
}
"""
source=original.replace('using namespace AuroraComposer;',helper+'\nusing namespace AuroraComposer;')
source,n=re.subn(r'(API\s+([A-Za-z_]\w*)\([^;]*?\)\s*\{)',lambda m:m[1]+' native_trace_006("'+m[2]+'",0);',source)
assert n==33,n
old='if (AuroraOpenDisplayDrm(&state.drm, 1)) return FAIL;'
assert source.count(old)==1
source=source.replace(old,'int opened=AuroraOpenDisplayDrm(&state.drm,1); native_trace_006("AuroraOpenDisplayDrm",opened); if(opened)return FAIL;')
source=source.replace('fail:\n    for (auto &buffer', 'fail:\n    native_trace_006("initialize_buffer_failure",-1);\n    for (auto &buffer')
src=work/'composer-trace.cpp';src.write_text(source)
tool=root/'window-bridge/toolchain';prefix=root/'prefix/system'
provider=root/'original-graphics-provider-002'
output=work/'libdisplay_composer_vdi_impl.z.so'
command=[str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-I'+str(ref),'-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(src),str(provider/'drm_device.o'),str(provider/'bundle/libdrm.so.2'),'-Wl,--no-undefined,-soname,libdisplay_composer_vdi_impl.z.so','-Wl,-rpath,/vendor/lib64/harmony-graphics','-o',str(output)]
r=subprocess.run(command,capture_output=True,text=True)
(local/'composer-compile.stdout').write_text(r.stdout);(local/'composer-compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
target='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
assert target in entries
entries[target]=(entries[target][0],output.read_bytes())
assert reference.read_text()==original
with (local/'composer-instrumentation.json').open('x') as f:
 json.dump(dict(reference_sha256=sha(reference),generated_source_sha256=sha(src),output_sha256=sha(output),command=command,api_entries=n,changes='diagnostics only; original return values and credentials preserved'),f,indent=2)
'''
payload=previous['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
anchor='assert all(entries[n]==v for n,v in original_entries.items())'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'\n'+instrument)
payload=payload.replace('native-original-graphics-boot-005','native-original-graphics-boot-006')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

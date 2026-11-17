"""Implement the original composer backlight entrypoints using real panel sysfs."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
BUILD=Path('/home/zoinve/harmony-virgl-883')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def adapt(source):
    old='API GetDisplayBacklight(uint32_t, uint32_t *) { native_trace_007("GetDisplayBacklight",0); return UNSUPPORTED; }\nAPI SetDisplayBacklight(uint32_t, uint32_t) { native_trace_007("SetDisplayBacklight",0); return UNSUPPORTED; }'
    assert source.count(old)==1
    new='''#include "native-backlight-129.h"
API GetDisplayBacklight(uint32_t device, uint32_t *level)
{ native_trace_007("GetDisplayBacklight",0); return NativeBacklight129::get(device,level); }
API SetDisplayBacklight(uint32_t device, uint32_t level)
{ native_trace_007("SetDisplayBacklight",0); return NativeBacklight129::set(device,level); }'''
    return source.replace(old,new,1)

if __name__=='__main__':
    work=BUILD/'commercial-composer-129'
    report=ROOT/'reports/commercial-composer-129'
    assert not work.exists() and not report.exists()
    parent=BUILD/'commercial-composer-075'
    metadata=json.loads((ROOT/'reports/commercial-composer-075/result.json').read_text())
    old=parent/'composer-evidence-075.cpp'
    previous=parent/'libdisplay_composer_vdi_impl.z.so'
    assert sha(old)==metadata['source_sha256'] and sha(previous)==metadata['composer_sha256']
    work.mkdir();report.mkdir()
    source=work/'composer-backlight-129.cpp'
    source.open('x').write(adapt(old.read_text()))
    command=list(metadata['command'])
    command[command.index(str(old))]=str(source)
    output=work/'libdisplay_composer_vdi_impl.z.so'
    command[command.index('-o')+1]=str(output)
    obj=work/'gaokun-basic-sysfs-001.o'
    compile_c=['clang-19','--target=aarch64-linux-ohos',
        '--sysroot='+str(BUILD/'sdk/native/sysroot'),
        '-resource-dir='+str(BUILD/'sdk/native/llvm/lib/clang/15.0.4'),
        '-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-fvisibility=hidden','-c',
        str(BASE/'gaokun-basic-sysfs-001.c'),'-o',str(obj)]
    compiled=subprocess.run(compile_c,capture_output=True)
    (report/'compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode==0,compiled.stderr.decode(errors='replace')
    command.insert(command.index(str(source))+1,str(obj))
    linked=subprocess.run(command,capture_output=True,timeout=120)
    (report/'link.stdout').open('xb').write(linked.stdout)
    (report/'link.stderr').open('xb').write(linked.stderr)
    assert linked.returncode==0,linked.stderr.decode(errors='replace')
    def symbols(path):return sorted(line.split()[-1] for line in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(path)],text=True).splitlines())
    assert symbols(output)==symbols(previous)
    trace=linked.stdout.decode()
    assert '/platform-root/' not in trace
    assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
    assert sha(old)==metadata['source_sha256'] and sha(previous)==metadata['composer_sha256']
    result=dict(command=command,compile_c=compile_c,composer_sha256=sha(output),composer_bytes=output.stat().st_size,
        source_sha256=sha(source),parent_composer_sha256=sha(previous),public_exports_unchanged=True,
        backend_sha256=sha(BASE/'gaokun-basic-sysfs-001.c'),header_sha256=sha(BASE/'native-backlight-129.h'),
        native_hdi_maximum=65535,real_panel_maximum_read_at_call=True,only_backlight_entrypoints_changed=True,
        original_gpu_composition_and_capture_unchanged=True,sdk_runtime_libraries_used=False,
        original_artifacts_unchanged=True,target_runtime_verified=False)
    for folder in [work,report]:(folder/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

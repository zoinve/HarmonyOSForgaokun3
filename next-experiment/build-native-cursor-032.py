"""Compile an independent native cursor bridge without installing or booting it."""
import subprocess,sys
payload=r'''
from pathlib import Path
import subprocess,hashlib,json,shutil
root=Path('/home/zoinve/harmony-virgl-883');project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
base=project/'next-experiment';work=root/'native-cursor-032-r2';local=project/'reports/native-cursor-032-r2'
if RESUME:
 assert work.is_dir() and local.is_dir() and not (work/'result.json').exists()
else:
 assert not work.exists() and not local.exists()
 work.mkdir();local.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=root/'native-original-graphics-boot-031/composer-trace.cpp';before=sha(old)
original=root/'native-touchpad-statusbar-032/libcursor_drawing_adapter.z.so'
assert sha(original)=='03e64bcecc882791855ec26840cfbfc8c4763e40e0e1612a677fd0d52b335d3e'
shutil.copyfile(original,work/'libcursor_drawing_adapter032.z.so')
source=old.read_text()
def replace(a,b):
 global source
 assert source.count(a)==1,a
 source=source.replace(a,b,1)
replace('using namespace AuroraComposer;','#include "native-cursor-state-032.h"\nusing namespace AuroraComposer;')
replace('    std::thread ticker;','    std::thread ticker;\n    std::thread cursor_ticker;\n    CursorWire032 *cursor_wire=nullptr;\n    std::vector<unsigned char> cursor_background;')
replace('int initialize()','static void cursor_tick_032();\nint initialize()')
replace('    return OK;\nfail:','    if(!state.cursor_ticker.joinable())state.cursor_ticker=std::thread(cursor_tick_032);\n    return OK;\nfail:')
replace('int wait_fence(int fence)','#include "native-cursor-composer-032.h"\nint wait_fence(int fence)')
replace('    cached_landscape_copy_024(static_cast<unsigned char *>(output.map),output.pitch,',
 '    state.cursor_background.resize(size_t(output.pitch)*state.drm.mode.vdisplay);\n    cached_landscape_copy_024(state.cursor_background.data(),output.pitch,')
replace('    if(trace)for(uint32_t y=0;', '    bool cursor_painted032=paint_cursor_032(output);\n    if(trace)for(uint32_t y=0;')
replace('    return result || output_result ? FAIL : OK;','    return result || output_result || !cursor_painted032 ? FAIL : OK;')
replace('    if (ticker.joinable()) ticker.join();','    if (ticker.joinable()) ticker.join();\n    if (cursor_ticker.joinable()) cursor_ticker.join();\n    if(cursor_wire)munmap(cursor_wire,64);')
(work/'composer-trace.cpp').write_text(source)
tool=root/'window-bridge/toolchain/ohos-platform-cxx'
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
prefix=root/'prefix/system';provider=root/'original-graphics-provider-002'
common=[str(tool),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-I'+str(base),'-I'+str(old.parent),'-Wl,--no-undefined']
commands=[common+[str(base/'native-cursor-adapter-032.cpp'),'-ldl','-Wl,-soname,libcursor_drawing_adapter.z.so','-o',str(work/'libcursor_drawing_adapter.z.so')],
 common+['-I'+str(ref),'-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm'),str(work/'composer-trace.cpp'),str(provider/'drm_device.o'),str(provider/'bundle/libdrm.so.2'),'-Wl,-soname,libdisplay_composer_vdi_impl.z.so','-Wl,-rpath,/vendor/lib64/harmony-graphics','-o',str(work/'libdisplay_composer_vdi_impl.z.so')]]
for i,c in enumerate(commands):
 r=subprocess.run(c,capture_output=True,text=True)
 attempt=0
 while (local/f'compile-{i}-{attempt}.stdout').exists():attempt+=1
 (local/f'compile-{i}-{attempt}.stdout').write_text(r.stdout);(local/f'compile-{i}-{attempt}.stderr').write_text(r.stderr)
 assert r.returncode==0,r.stderr
assert sha(old)==before
names=['libcursor_drawing_adapter.z.so','libcursor_drawing_adapter032.z.so','libdisplay_composer_vdi_impl.z.so','composer-trace.cpp']
result=dict(sha256={n:sha(work/n) for n in names},original_adapter_sha256=sha(original),original_composer_unchanged=True,input_injection=False,installed=False,runtime_verified=False,commands=commands)
for p in [work/'result.json',local/'result.json']:p.write_text(json.dumps(result,indent=2))
for n in names:shutil.copyfile(work/n,local/n)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input='RESUME='+repr('--resume-compile' in sys.argv)+'\n'+payload,text=True,timeout=180).returncode)

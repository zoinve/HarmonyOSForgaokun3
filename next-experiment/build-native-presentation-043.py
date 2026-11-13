"""Build-only completion telemetry beside, never over, the existing 041 pipeline."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,re,runpy,shutil,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
old=root/'native-render-041';work=root/'native-presentation-043'
local=base.parent/'reports/native-presentation-043'
assert not work.exists() and not local.exists()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=json.loads((old/'result.json').read_text())
for name,digest in baseline['sha256'].items(): assert sha(old/name)==digest,name
assert (old/'composer-trace.cpp').read_bytes()==(base.parent/'reports/native-render-041/composer-trace.cpp').read_bytes()
assert (old/'native-cursor-composer-041.h').read_bytes()==(base.parent/'reports/native-render-041/native-cursor-composer-041.h').read_bytes()
command=list(baseline['commands'][0])
roots=[Path(x[2:]) for x in command if x.startswith('-I')]
guarded={}
def guard(path):
 path=Path(path).resolve();guarded[str(path)]=sha(path);return path
for path in [old/'result.json',old/'native-cursor-composer-041.h',base/'native-presentation-043.py',
             base/'native-presentation-043.h',Path(command[0])]: guard(path)
for name in baseline['sha256']: guard(old/name)
for arg in command:
 if not arg.startswith('-') and Path(arg).is_file(): guard(arg)
visited=set()
def quoted_headers(path):
 path=guard(path)
 if path in visited:return
 visited.add(path)
 for name in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(),re.M):
  candidates=[path.parent/name]+[directory/name for directory in roots]
  found=next((p for p in candidates if p.is_file()),None)
  assert found is not None,(str(path),name)
  quoted_headers(found)
quoted_headers(old/'composer-trace.cpp')
quoted_headers(old/'native-cursor-composer-041.h')
work.mkdir();local.mkdir()
adapter=runpy.run_path(str(base/'native-presentation-043.py'))
original=(old/'composer-trace.cpp').read_text();cursor=(old/'native-cursor-composer-041.h').read_text()
traced,traced_cursor=adapter['adapt'](original,cursor)
assert adapter['strip'](traced,traced_cursor)==(original,cursor)
assert traced.count('#include "native-cursor-composer-041.h"')==1
traced=traced.replace('#include "native-cursor-composer-041.h"','#include "native-cursor-composer-043.h"')
(work/'composer-trace.cpp').write_text(traced)
(work/'native-cursor-composer-043.h').write_text(traced_cursor)
shutil.copyfile(base/'native-presentation-043.h',work/'native-presentation-043.h')
# Freeze the current project-owned headers locally; historical 041 did not pin
# every header, so this is not a claim of byte-equivalence to its historical ELF.
for path in visited:
 if path.parent==base.resolve() and path.suffix=='.h': shutil.copyfile(path,work/path.name)
command=[str(work/'composer-trace.cpp') if x==str(old/'composer-trace.cpp') else
         str(work/'libdisplay_composer_vdi_impl.z.so') if x==str(old/'libdisplay_composer_vdi_impl.z.so') else x
         for x in command]
command.insert(1,'-I'+str(work))
(local/'command.json').write_text(json.dumps(command,indent=2))
with (local/'compile.stdout').open('xb') as out,(local/'compile.stderr').open('xb') as err:
 result=subprocess.run(command,stdout=out,stderr=err,timeout=180)
assert result.returncode==0,result.returncode
elf=work/'libdisplay_composer_vdi_impl.z.so'
b=elf.read_bytes();assert b[:6]==b'\x7fELF\x02\x01' and int.from_bytes(b[18:20],'little')==183
def symbols(path):
 r=subprocess.run(['llvm-nm-19','-D','--defined-only',str(path)],text=True,capture_output=True,check=True)
 return r.stdout,{line.split()[-1] for line in r.stdout.splitlines() if len(line.split())>=3}
old_nm,old_names=symbols(old/'libdisplay_composer_vdi_impl.z.so')
new_nm,new_names=symbols(elf)
public={name for name in old_names if not name.startswith('_')}
assert public and public<=new_names,sorted(public-new_names)
(local/'exports.txt').write_text(new_nm)
dynamic=subprocess.run(['readelf','-dW',str(elf)],text=True,capture_output=True,check=True).stdout
assert not any(bad in dynamic for bad in ('libc.so.6','libstdc++','libgcc_s'))
(local/'dynamic.txt').write_text(dynamic)
for path, digest in guarded.items(): assert sha(path)==digest,path
names=['composer-trace.cpp','native-cursor-composer-043.h','native-presentation-043.h','libdisplay_composer_vdi_impl.z.so']
for name in names:shutil.copyfile(work/name,local/name)
data=dict(files={name:dict(path=str(work/name),bytes=(work/name).stat().st_size,sha256=sha(work/name)) for name in names},
 guarded_inputs=guarded,command=command,baseline041_unchanged=True,reversible_source_change=True,
 required_c_exports_verified=sorted(public),timestamp_source='Actual KMS page_flip_handler arguments; capability query records clock domain',
 sampling='4096 records; 16-completion batches; abrupt exit can lose final batch; instrumentation is not an FPS benchmark',
 submission_ids_are_visual_content_ids=False,initial_modesets_counted=False,input_injection=False,
 installed=False,runtime_verified=False,desktop_fps_verified=False,physical_board_test=False)
for p in [work/'result.json',local/'result.json']:
 with p.open('x') as f:json.dump(data,f,indent=2)
print(json.dumps(data,indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

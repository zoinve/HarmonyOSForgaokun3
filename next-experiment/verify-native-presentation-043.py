"""Read-only independent artifact audit; no device access or target execution."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,runpy,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
local=project/'reports/native-presentation-043'
report=project/'reports/native-presentation-043-independent'
assert not report.exists()
report.mkdir()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
manifest=local/'result.json'
d=json.loads(manifest.read_text())
assert sha(manifest)==sha(root/'native-presentation-043/result.json')
for name,row in d['files'].items():
 assert Path(name).name==name
 for p in (Path(row['path']),local/name):
  assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for p,digest in d['guarded_inputs'].items():assert sha(p)==digest,p
work=root/'native-presentation-043'
frozen=0
for p,digest in d['guarded_inputs'].items():
 p=Path(p)
 if p.parent==project/'next-experiment' and p.suffix=='.h':
  assert sha(work/p.name)==digest,p
  frozen+=1
adapter=runpy.run_path(str(project/'next-experiment/native-presentation-043.py'))
text=(work/'composer-trace.cpp').read_text()
old_include='#include "native-cursor-composer-041.h"'
new_include='#include "native-cursor-composer-043.h"'
assert text.count(new_include)==1
restored=adapter['strip'](text.replace(new_include,old_include),(work/'native-cursor-composer-043.h').read_text())
baseline=root/'native-render-041'
assert restored==((baseline/'composer-trace.cpp').read_text(),(baseline/'native-cursor-composer-041.h').read_text())
elf=work/'libdisplay_composer_vdi_impl.z.so'
b=elf.read_bytes()
assert b[:6]==b'\x7fELF\x02\x01' and int.from_bytes(b[16:18],'little')==3 and int.from_bytes(b[18:20],'little')==183
dynamic=subprocess.run(['readelf','-dW',str(elf)],capture_output=True,text=True,check=True).stdout
assert '(SONAME)' in dynamic and 'libdisplay_composer_vdi_impl.z.so' in dynamic
assert not any(x in dynamic for x in ('libc.so.6','libstdc++','libgcc_s'))
symbols=subprocess.run(['llvm-nm-19','-D','--defined-only',str(elf)],capture_output=True,text=True,check=True).stdout
names={line.split()[-1] for line in symbols.splitlines() if len(line.split())>=3}
required=set(d['required_c_exports_verified'])
assert required and required<=names
existing=project/'reports/native-original-graphics-boot-041/runtime-evidence'
retrieval=json.loads((existing/'retrieval-manifest.json').read_text())
assert len(retrieval['files'])==71
old_markers=0
for name,row in retrieval['files'].items():
 assert Path(name).name==name
 p=existing/'raw'/name
 assert not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 old_markers+=p.read_bytes().count(b'NATIVE_PRESENT043 ')
for p,digest in d['guarded_inputs'].items():assert sha(p)==digest,p
for name,content in [('dynamic.txt',dynamic),('exports.txt',symbols)]:
 with (report/name).open('x') as f:f.write(content)
result=dict(manifest_sha256=sha(manifest),files_verified=d['files'],
 guarded_inputs_verified=len(d['guarded_inputs']),frozen_header_copies_verified=frozen,
 source_reversal_verified=True,aarch64_shared_elf_verified=True,
 required_c_exports_verified=len(required),existing_native041_raw_files_verified=71,
 existing_native041_marker043_count=old_markers,existing_native041_is_not_a_new_run=True,
 historical041_full_header_provenance_available=False,
 runtime_dependency_closure_verified=False,target_code_executed=False,device_accessed=False,
 installed_by_this_audit=False,stable_120fps_verified=False)
with (report/'result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='files_verified'},indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

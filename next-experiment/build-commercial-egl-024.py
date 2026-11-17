"""Offline relink of our bridge only; never installs or boots the device."""
from pathlib import Path
import subprocess

payload=r'''
from pathlib import Path
import hashlib,json,runpy,subprocess,shutil
base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
old=root/'commercial-graphics-014'
work=root/'commercial-egl-024'
local=base/'reports/commercial-egl-024'
assert not work.exists() and not local.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=old/'egl-commercial-014.cpp';original=old/'libEGL_impl.so'
before={str(p):sha(p) for p in [source,original,old/'result.json']}
assert sha(original)=='83de7308499d873466a90f84c1762ba9c57c2e7d87ba9403b5eab01c601f1e60'
manifest=json.loads((old/'result.json').read_text())
command=runpy.run_path(str(base/'next-experiment/commercial-egl-binding-024.py'))['isolate_command'](manifest['commands'][1],work/'libEGL_impl.so')
work.mkdir();local.mkdir()
with (work/'link.stdout').open('xb') as out,(work/'link.stderr').open('xb') as err:
 subprocess.run(command,stdout=out,stderr=err,check=True,timeout=120)
trace=(work/'link.stdout').read_text()
assert '/platform-root/' not in trace
assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
def symbols(p):
 text=subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(p)],text=True)
 return sorted(line.split()[-1] for line in text.splitlines())
new=work/'libEGL_impl.so'
assert symbols(new)==symbols(original), 'public bridge exports must remain unchanged'
def display_code(p):
 return subprocess.check_output(['aarch64-linux-gnu-objdump','-d','--disassemble=eglGetDisplay',str(p)],text=True)
old_code=display_code(original);new_code=display_code(new)
assert 'eglGetPlatformDisplayEXT@plt' in old_code
assert 'eglGetPlatformDisplayEXT@plt' not in new_code
assert '<eglGetPlatformDisplayEXT>' in new_code
for p,digest in before.items():assert sha(Path(p))==digest,p
result=dict(command=command,source_sha256=sha(source),original_bridge_sha256=sha(original),
 bridge_sha256=sha(new),bridge_bytes=new.stat().st_size,public_exports_unchanged=True,
 original_self_call_via_plt=True,new_self_call_locally_bound=True,
 sdk_runtime_libraries_used=False,original_artifacts_unchanged=True,
 device_installed=False,target_runtime_verified=False,desktop_verified=False)
for name,text in [('old-eglGetDisplay.txt',old_code),('new-eglGetDisplay.txt',new_code),('result.json',json.dumps(result,indent=2))]:
 with (work/name).open('x') as f:f.write(text)
for name in ['link.stdout','link.stderr','old-eglGetDisplay.txt','new-eglGetDisplay.txt','result.json']:
 shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

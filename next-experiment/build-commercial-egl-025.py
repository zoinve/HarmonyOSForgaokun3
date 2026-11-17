"""Build a diagnostic-only own bridge; no device access or original writes."""
from pathlib import Path
import subprocess

payload=r'''
from pathlib import Path
import hashlib,json,runpy,subprocess,shutil
base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-egl-025';local=base/'reports/commercial-egl-025'
assert not work.exists() and not local.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=root/'commercial-graphics-014/egl-commercial-014.cpp'
previous=root/'commercial-egl-024/libEGL_impl.so'
manifest=json.loads((base/'reports/commercial-egl-024/result.json').read_text())
assert sha(old)==manifest['source_sha256']
assert sha(previous)==manifest['bridge_sha256']
source=runpy.run_path(str(base/'next-experiment/commercial-egl-trace-025.py'))['instrument'](old.read_text())
work.mkdir();local.mkdir()
new_source=work/'egl-trace-025.cpp'
new_source.write_text(source)
command=list(manifest['command'])
assert command.count(str(old))==1
command[command.index(str(old))]=str(new_source)
command[command.index('-o')+1]=str(work/'libEGL_impl.so')
with (work/'link.stdout').open('xb') as out,(work/'link.stderr').open('xb') as err:
 subprocess.run(command,stdout=out,stderr=err,check=True,timeout=120)
trace=(work/'link.stdout').read_text()
assert '/platform-root/' not in trace
assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
def symbols(p):
 return sorted(line.split()[-1] for line in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(p)],text=True).splitlines())
new=work/'libEGL_impl.so'
assert symbols(new)==symbols(previous)
assert sha(old)==manifest['source_sha256'] and sha(previous)==manifest['bridge_sha256']
result=dict(command=command,source_sha256=sha(new_source),original_source_sha256=sha(old),
 bridge_sha256=sha(new),bridge_bytes=new.stat().st_size,previous_bridge_sha256=sha(previous),
 public_exports_unchanged=True,sdk_runtime_libraries_used=False,original_artifacts_unchanged=True,
 diagnostic_only=True,per_process_log_limit=64,target_runtime_verified=False,desktop_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2))
for name in ['egl-trace-025.cpp','link.stdout','link.stderr','result.json']:
 shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':
 raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

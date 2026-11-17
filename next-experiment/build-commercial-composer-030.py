"""Build only bounded real-buffer diagnostics against the original commercial ABI."""
import subprocess
payload=r'''
from pathlib import Path
import hashlib,json,runpy,subprocess,shutil
base=Path('/mnt/d/lab/HarmonyOSForMatebookego');root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-composer-030';local=base/'reports/commercial-composer-030'
assert not work.exists() and not local.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=root/'commercial-graphics-014/composer-trace.cpp'
previous=root/'commercial-graphics-014/libdisplay_composer_vdi_impl.z.so'
manifest=json.loads((base/'reports/commercial-graphics-014/result.json').read_text())
assert sha(previous)=='31de3d40703ed457e1e2e4420dd3e8e37be87a62820a422a72d61798ea6f3a38'
old_source_sha=sha(old)
source=runpy.run_path(str(base/'next-experiment/commercial-frame-evidence-030.py'))['instrument'](old.read_text())
work.mkdir();local.mkdir()
new_source=work/'composer-evidence-030.cpp';new_source.write_text(source)
command=list(manifest['commands'][0]);assert command.count(str(old))==1
command[command.index(str(old))]=str(new_source)
new=work/'libdisplay_composer_vdi_impl.z.so';command[command.index('-o')+1]=str(new)
with (work/'link.stdout').open('xb') as out,(work/'link.stderr').open('xb') as err:
 subprocess.run(command,stdout=out,stderr=err,check=True,timeout=120)
trace=(work/'link.stdout').read_text()
assert '/platform-root/' not in trace
assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
def symbols(p):return sorted(line.split()[-1] for line in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(p)],text=True).splitlines())
assert symbols(new)==symbols(previous)
assert sha(old)==old_source_sha and sha(previous)=='31de3d40703ed457e1e2e4420dd3e8e37be87a62820a422a72d61798ea6f3a38'
result=dict(command=command,composer_sha256=sha(new),composer_bytes=new.stat().st_size,
 previous_composer_sha256=sha(previous),original_source_sha256=old_source_sha,source_sha256=sha(new_source),
 public_exports_unchanged=True,sdk_runtime_libraries_used=False,original_artifacts_unchanged=True,
 diagnostic_only=True,max_captures=128,subsequent_capture_interval_us=1000000,
 target_runtime_verified=False,desktop_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2))
for name in ['composer-evidence-030.cpp','link.stdout','link.stderr','result.json']:shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

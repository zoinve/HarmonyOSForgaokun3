"""Fresh offline archive: native profile003 + immutable OHOS fence bundle + render sandbox."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-diagnostic-init-009.py'))
source=runpy.run_path(str(base/'baremetal-diagnostic-mesa-010.py'))['build_source'](parent['source'])
old=parent['payload'];payload='source='+repr(source)+'\n'+old[old.index('\nfrom pathlib import Path')+1:]
assert 'baremetal-diagnostic-init-009' in payload
payload=payload.replace('baremetal-diagnostic-init-009','baremetal-diagnostic-init-010')
anchor="updated=raw[:trailer]+member('init'"
assert payload.count(anchor)==1
extras=r'''
import tarfile,io
manifest=json.loads((project/'reports/baremetal-freedreno-fence-package-001/package.json').read_text())
bundle=project/'reports/baremetal-freedreno-fence-package-001/bundle.tar.gz'
assert sha(bundle)==manifest['archive_sha256'] and bundle.stat().st_size==manifest['archive_bytes']
assert manifest['all_strong_dynamic_symbols_resolved'] and len(manifest['files'])==9
expected={row['path']:row for row in manifest['files']};contents={}
with tarfile.open(bundle,'r:gz') as tar:
 for item in tar.getmembers():
  name=item.name.removeprefix('./')
  if item.isdir():
   assert name in ['lib','lib/gbm'];continue
  if item.issym():
   assert name=='lib/libc.so' and item.linkname=='ld-musl-aarch64.so.1';continue
  assert item.isfile() and (name in expected or name=='manifest.json'),name
  data=tar.extractfile(item).read()
  if name=='manifest.json':continue
  assert name not in contents and len(data)==expected[name]['bytes'] and hashlib.sha256(data).hexdigest()==expected[name]['sha256']
  contents[name]=data
assert contents.keys()==expected.keys()
launcher_source=base/'baremetal-mesa-launcher-001.c'
(work/launcher_source.name).write_bytes(launcher_source.read_bytes())
r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/launcher_source.name),'-o',str(work/'mesa-launcher')],capture_output=True,text=True,timeout=90)
(local/'launcher-compile.stdout').write_text(r.stdout);(local/'launcher-compile.stderr').write_text(r.stderr);assert r.returncode==0,r.stderr
additions=[]
for name in ['opt','opt/native-mesa-001','opt/native-mesa-001/lib','opt/native-mesa-001/lib/gbm']:
 if name not in old:additions.append((name,stat.S_IFDIR|0o755,b''))
for name,data in contents.items():additions.append(('opt/native-mesa-001/'+name,stat.S_IFREG|0o555,data))
additions.append(('opt/native-mesa-001/lib/libc.so',stat.S_IFLNK|0o777,b'ld-musl-aarch64.so.1'))
additions.append(('bin/native-mesa-launcher-001',stat.S_IFREG|0o755,(work/'mesa-launcher').read_bytes()))
assert len({name for name,mode,data in additions})==len(additions) and not any(name in old for name,mode,data in additions)
extra=b''.join(member(name,mode,data,0x200000+i) for i,(name,mode,data) in enumerate(additions))
'''
payload=payload.replace(anchor,extras+"\nupdated=raw[:trailer]+extra+member('init'")
assert payload.count('len(seen)==len(old)+2')==1
payload=payload.replace('len(seen)==len(old)+2','len(seen)==len(old)+2+len(additions)')
anchor="(work/'result.json').write_text(json.dumps(d,indent=2)+'\\n');"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"d.update(mesa_bundle_archive_sha256=sha(bundle),mesa_bundle_files=manifest['files'],launcher_sha256=sha(work/'mesa-launcher'),launcher_source_sha256=sha(launcher_source),new_entry_count=len(additions)+2,mesa_gpu_execution_verified=False,selinux_policy_loaded_by_diagnostic=False)\n"+anchor)
compile(payload,'native-mesa-diagnostic-010-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

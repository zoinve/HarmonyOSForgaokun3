"""Archive verified native build products to the isolated lab partition only."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
report_path = base / 'reports/baremetal-native-build-staged-001.json'
assert not report_path.exists()

pack = r'''
from pathlib import Path
import hashlib,json,tarfile
work=Path('/home/zoinve/harmony-virgl-883/baremetal-native-build-001')
build=work/'out';report=json.loads((work/'result.json').read_text())
assert report['build_success'] and report['critical_source_files_unchanged']
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for row in report['artifacts']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
archive=work/'native-artifacts.tar.gz';manifest_path=work/'native-artifacts-manifest.json'
assert not archive.exists() and not manifest_path.exists()
modules=sorted(build.rglob('*.ko'));assert len(modules)==report['module_count']==391
names=[Path(row['path']) for row in report['artifacts']]+[build/'.config']+modules
for name in ['modules.builtin.modinfo','include/config/kernel.release']:
 p=build/name
 if p.is_file():names.append(p)
rows=[]
with tarfile.open(archive,'x:gz',compresslevel=1) as tar:
 for p in names:
  assert p.is_file() and not p.is_symlink()
  name=p.relative_to(build).as_posix()
  rows.append(dict(name=name,bytes=p.stat().st_size,sha256=sha(p)))
  tar.add(p,arcname=name,recursive=False)
for row in rows:assert sha(build/row['name'])==row['sha256']
manifest=dict(source_commit=report['source_commit'],files=rows,module_count=len(modules),
              archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),
              package_layout='uninstalled kernel build products; not a boot entry',
              kernel_release=(build/'include/config/kernel.release').read_text().strip(),
              harmony_identity_patch_applied=False)
manifest_path.write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest))
'''
compile(pack, 'pack-native-artifacts', 'exec')
r = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=pack,
                   text=True, capture_output=True, check=True, timeout=600)
manifest = json.loads(r.stdout)

prepare = r'''
from pathlib import Path
import json,subprocess
root=Path('/mnt/harmony-lab/work')
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(root)],text=True).strip()=='/dev/nvme0n1p4'
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(root)],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
out=root/'native-build-001';assert not out.exists();out.mkdir()
'''
compile(prepare, 'prepare-native-staging', 'exec')
subprocess.run(['ssh', 'matebook', 'python3 -'], input=prepare,
               text=True, check=True, timeout=30)
source = Path(r'\\wsl.localhost\Debian\home\zoinve\harmony-virgl-883\baremetal-native-build-001')
remote = '/mnt/harmony-lab/work/native-build-001'
for name in ['native-artifacts.tar.gz', 'native-artifacts-manifest.json']:
    subprocess.run(['scp', str(source / name), 'matebook:' + remote + '/' + name],
                   check=True, timeout=600)

verify = r'''
from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path('/mnt/harmony-lab/work/native-build-001')
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(root)],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
m=json.loads((root/'native-artifacts-manifest.json').read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=root/'native-artifacts.tar.gz'
assert p.stat().st_size==m['archive_bytes'] and sha(p)==m['archive_sha256']
out=root/'artifacts';assert not out.exists();out.mkdir()
with tarfile.open(p,'r:gz') as tar:
 members=tar.getmembers()
 assert len(members)==len(m['files'])
 assert all(x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in members)
 tar.extractall(out,filter='data')
for row in m['files']:
 p=out/row['name'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert sum(1 for _ in out.rglob('*.ko'))==m['module_count']
result=dict(destination=str(out),files_verified=len(m['files']),module_count=m['module_count'],
            archive_sha256=m['archive_sha256'],kernel_release=m['kernel_release'],
            installed_to_host=False,boot_entries_modified=False,native_boot_attempted=False,
            harmony_identity_patch_applied=False)
(root/'staging-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
compile(verify, 'verify-native-staging', 'exec')
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=verify,
                   text=True, capture_output=True, check=True, timeout=600)
result = json.loads(r.stdout)
assert result['archive_sha256'] == manifest['archive_sha256']
report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(r.stdout)

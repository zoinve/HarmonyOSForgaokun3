"""Independently inspect all archive records including the original nine OHOS Mesa ELF files."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-diagnostic-init-009.py')))['payload']
payload=payload.replace('baremetal-diagnostic-init-009','baremetal-diagnostic-init-010')
old="old=archive(parent);new=archive(p);assert set(new)-set(old)=={'init','bin/native-identity-read-002'} and set(old)<=set(new)"
new="""old=archive(parent);new=archive(p)
manifest=json.loads((project/'reports/baremetal-freedreno-fence-package-001/package.json').read_text())
expected={'init','bin/native-identity-read-002','bin/native-mesa-launcher-001','opt','opt/native-mesa-001','opt/native-mesa-001/lib','opt/native-mesa-001/lib/gbm','opt/native-mesa-001/lib/libc.so'}
expected.update('opt/native-mesa-001/'+row['path'] for row in manifest['files'])
assert set(new)-set(old)==expected and len(expected)==17 and set(old)<=set(new)
for row in manifest['files']:
 mode,uid,gid,data=new['opt/native-mesa-001/'+row['path']]
 assert stat.S_ISREG(mode) and mode&0o777==0o555 and uid==gid==0 and len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert new['opt/native-mesa-001/lib/libc.so']==(stat.S_IFLNK|0o777,0,0,b'ld-musl-aarch64.so.1')
launcher=p.parent/'mesa-launcher'
assert new['bin/native-mesa-launcher-001'][3]==launcher.read_bytes() and sha(launcher)==meta['launcher_sha256']
assert sha(project/'next-experiment/baremetal-mesa-launcher-001.c')==meta['launcher_source_sha256']
assert sha(project/'reports/baremetal-freedreno-fence-package-001/bundle.tar.gz')==meta['mesa_bundle_archive_sha256']
"""
assert payload.count(old)==1
payload=payload.replace(old,new)
compile(payload,'independent-native-diag010','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=100)
    raise SystemExit(r.returncode)

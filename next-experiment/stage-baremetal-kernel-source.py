"""Snapshot a clean existing SC8280XP tree into the authorized lab partition."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
report = base / 'reports/baremetal-kernel-source-staged-001.json'
assert not report.exists(), 'Do not overwrite a completed staging record'
pack = r'''
from pathlib import Path
import gzip, hashlib, json, subprocess
source=Path('/home/zoinve/ego-kernel-diag-20261101/linux')
out=Path('/home/zoinve/harmony-virgl-883/baremetal-source-001')
assert not out.exists()
def git(*args):
    return subprocess.check_output(['git','-C',str(source),*args],text=True).strip()
assert git('status','--porcelain=v1') == ''
commit=git('rev-parse','HEAD')
assert commit == '415567fcecbe139c9e334b02958fc05dc3c674cc'
out.mkdir()
archive=out/'linux-source.tar.gz'
with archive.open('xb') as target:
    with gzip.GzipFile(filename='',fileobj=target,mode='wb',compresslevel=1,mtime=0) as packed:
        proc=subprocess.Popen(['git','-C',str(source),'archive','--format=tar',commit],stdout=subprocess.PIPE)
        while chunk:=proc.stdout.read(1024*1024): packed.write(chunk)
        assert proc.wait() == 0
assert git('status','--porcelain=v1') == '' and git('rev-parse','HEAD') == commit
critical=['drivers/android/binder.c','drivers/android/binder_internal.h',
          'include/uapi/linux/android/binder.h','include/linux/sched.h',
          'arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dts']
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
manifest=dict(source=str(source),commit=commit,tree=git('rev-parse','HEAD^{tree}'),
              source_clean_before_after=True,archive_bytes=archive.stat().st_size,
              archive_sha256=sha(archive),critical={name:sha(source/name) for name in critical})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
'''
r = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=pack,
                   text=True, capture_output=True, check=True)
manifest = json.loads(r.stdout)
remote = '/mnt/harmony-lab/work/kernel-source-001'
guard = """
from pathlib import Path
import subprocess
work=Path('/mnt/harmony-lab/work')
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(work)],text=True).strip() == '/dev/nvme0n1p4'
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(work)],text=True).strip() == '00029cdd-1748-4d2f-b73b-8e8164922098'
dest=work/'kernel-source-001'
assert not dest.exists()
dest.mkdir()
"""
subprocess.run(['ssh', 'matebook', 'python3 -'], input=guard, text=True, check=True)
local = Path(r'\\wsl.localhost\Debian\home\zoinve\harmony-virgl-883\baremetal-source-001')
for name in ('linux-source.tar.gz', 'manifest.json'):
    subprocess.run(['scp', str(local / name), 'matebook:' + remote + '/' + name], check=True)
verify = r'''
from pathlib import Path
import hashlib,json,tarfile,subprocess
dest=Path('/mnt/harmony-lab/work/kernel-source-001')
m=json.loads((dest/'manifest.json').read_text())
archive=dest/'linux-source.tar.gz'
assert archive.stat().st_size == m['archive_bytes']
with archive.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest() == m['archive_sha256']
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(dest)],text=True).strip() == '/dev/nvme0n1p4'
tree=dest/'linux';assert not tree.exists();tree.mkdir()
with tarfile.open(archive,'r:gz') as tar: tar.extractall(tree,filter='data')
for name,digest in m['critical'].items():
    assert hashlib.sha256((tree/name).read_bytes()).hexdigest() == digest,name
m.update(destination=str(tree),archive_verified=True,critical_files_verified=True,
         existing_source_modified=False,boot_entries_modified=False,native_boot_attempted=False)
(dest/'staging-result.json').write_text(json.dumps(m,indent=2))
print(json.dumps(m,indent=2))
'''
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=verify,
                   text=True, capture_output=True, check=True)
result = json.loads(r.stdout)
assert result['archive_sha256'] == manifest['archive_sha256']
report.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(r.stdout)

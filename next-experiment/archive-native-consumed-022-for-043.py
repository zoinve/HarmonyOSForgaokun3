"""Retire exactly one consumed experimental entry after a verified recoverable copy."""
from pathlib import Path
import json
import subprocess

ENTRY = 'loader/entries/native-original-graphics-022+0-1.conf'
IMAGE = 'native-original-graphics-022/initrd.img'


def retirement_plan(inventory):
    configs = inventory['configs']
    assert ENTRY in configs
    users = []
    for name, text in configs.items():
        for line in text.splitlines():
            fields = line.split()
            if fields and fields[0] in ('linux', 'initrd', 'devicetree'):
                if fields[1].lstrip('/') == IMAGE:
                    users.append(name)
    assert users == [ENTRY], users
    rows = {r['path']: r for r in inventory['files']}
    assert {p for p in rows if p.startswith('native-original-graphics-022/')} == {IMAGE}
    assert rows[IMAGE]['bytes'] == 31620517
    return {p: rows[p] for p in (ENTRY, IMAGE)}


REMOTE = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi')
entry='loader/entries/native-original-graphics-022+0-1.conf'
image='native-original-graphics-022/initrd.img'
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043/efi-archive-consumed-022')
def cmd(args): return subprocess.check_output(args,text=True,timeout=30)
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def rows():
 result=[]
 for p in sorted(esp.rglob('*')):
  if p.is_file():
   assert not p.is_symlink()
   result.append(dict(path=str(p.relative_to(esp)),bytes=p.stat().st_size,sha256=sha(p)))
 return result
def configs(): return {str(p.relative_to(esp)):p.read_text() for p in sorted((esp/'loader/entries').glob('*.conf'))}
def guards():
 assert os.getuid()==0
 assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==request['inventory']['boot_id']
 assert cmd(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
 assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
 assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
 assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
 status=cmd(['bootctl','status','--no-pager'])
 assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
 assert 'OneShot Entry:' not in status
 assert cmd(['efibootmgr','-v'])==request['inventory']['firmware']
 assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
 assert cmd(['systemctl','is-enabled','harmony-lab-screen-off-001.timer']).strip()=='enabled'
guards()
assert set(request['selected'])=={entry,image}
assert rows()==request['inventory']['files']
assert configs()==request['inventory']['configs']
assert list((esp/'native-original-graphics-022').iterdir())==[esp/image]
assert not archive.exists() and archive.parent.is_dir() and not archive.parent.is_symlink()
assert shutil.disk_usage(archive.parent).free>sum(r['bytes'] for r in request['selected'].values())+64*1024*1024
archive.mkdir(mode=0o700)
with (archive/'before.json').open('x') as f:
 json.dump(request,f,indent=2); f.flush(); os.fsync(f.fileno())
for name,row in request['selected'].items():
 src=esp/name; dst=archive/name
 assert src.is_file() and not src.is_symlink() and sha(src)==row['sha256']
 dst.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with src.open('rb') as fi, dst.open('xb') as fo:
  shutil.copyfileobj(fi,fo,1024*1024); fo.flush(); os.fsync(fo.fileno())
 assert dst.stat().st_size==row['bytes'] and sha(dst)==row['sha256']
for directory in sorted((p for p in archive.rglob('*') if p.is_dir()),reverse=True)+[archive]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
 try: os.fsync(fd)
 finally: os.close(fd)
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
for name,row in request['selected'].items(): assert sha(archive/name)==row['sha256']
# The only reference is the already-consumed +0-1 entry, not a usable/default entry.
users=[name for name,text in configs().items() for line in text.splitlines()
       if line.split() and line.split()[0] in ('linux','initrd','devicetree') and line.split()[1].lstrip('/')==image]
assert users==[entry]
(esp/entry).unlink()
assert all('/'+image not in text for text in configs().values())
(esp/image).unlink()
(esp/'native-original-graphics-022').rmdir()
os.sync()
guards()
after=rows()
assert after==[r for r in request['inventory']['files'] if r['path'] not in request['selected']]
after_configs=configs()
assert after_configs=={k:v for k,v in request['inventory']['configs'].items() if k!=entry}
free=shutil.disk_usage(esp).free
assert free>64*1024*1024+345590+65536
result=dict(boot_id=request['inventory']['boot_id'],archive=str(archive),archived_files=request['selected'],
 efi_files_after=after,configs_after=after_configs,firmware=request['inventory']['firmware'],
 efi_free_after=free,remaining_efi_files_unchanged=len(after),ubuntu_default_preserved=True,
 screenoff_timer_preserved=True,one_shot_absent=True,raw_runtime_logs_touched=False,
 removed_only_archived_efi_copies=True)
with (archive/'retirement-result.json').open('x') as f:
 json.dump(result,f,indent=2); f.flush(); os.fsync(f.fileno())
print(json.dumps(result))
'''

if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    out = base/'reports/native-presentation-043-efi-archive-022.json'
    assert not out.exists()
    inventory = json.loads((base/'reports/native-presentation-043-efi-inventory.json').read_text())
    selected = retirement_plan(inventory)
    assert inventory['efi_free']+sum(r['bytes'] for r in selected.values())>64*1024*1024+345590+65536
    request = dict(inventory=inventory, selected=selected)
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input='request='+repr(request)+'\n'+REMOTE,
                       text=True, capture_output=True, timeout=180)
    if r.returncode:
        raise RuntimeError(r.stderr)
    result = json.loads(r.stdout)
    with out.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(dict(archived_files=len(result['archived_files']),
                          remaining_efi_files_unchanged=result['remaining_efi_files_unchanged'],
                          efi_free_after=result['efi_free_after'], archive=result['archive'])))

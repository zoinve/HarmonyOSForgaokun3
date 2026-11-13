"""Fresh read-only EFI inventory; does not archive, delete or select an entry."""
from pathlib import Path
import json
import subprocess

REMOTE = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
def cmd(args): return subprocess.check_output(args,text=True,timeout=30)
def sha(p):
 with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
esp=Path('/boot/efi')
assert os.getuid()==0
assert cmd(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
status=cmd(['bootctl','status','--no-pager'])
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
assert 'OneShot Entry:' not in status
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
assert cmd(['systemctl','is-enabled','harmony-lab-screen-off-001.timer']).strip()=='enabled'
configs={str(p.relative_to(esp)):p.read_text() for p in sorted((esp/'loader/entries').glob('*.conf'))}
files=[]
for p in sorted(esp.rglob('*')):
 if p.is_file():
  assert not p.is_symlink()
  files.append(dict(path=str(p.relative_to(esp)),bytes=p.stat().st_size,sha256=sha(p)))
lab=subprocess.run(['findmnt','-n','--mountpoint','/mnt/harmony-lab'],capture_output=True,text=True,timeout=15)
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 kernel=cmd(['uname','-r']).strip(),efi_free=shutil.disk_usage(esp).free,
 home_free=shutil.disk_usage('/home/zoinve').free,files=files,configs=configs,
 bootctl=status,firmware=cmd(['efibootmgr','-v']),lab_mount=lab.stdout,
 stage_exists=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043').exists(),
 screenoff_timer_active_enabled=True,read_only=True),indent=2))
'''

if __name__ == '__main__':
    out = Path(__file__).resolve().parents[1] / 'reports/native-presentation-043-efi-inventory.json'
    assert not out.exists()
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=REMOTE,
                       text=True, capture_output=True, timeout=120)
    r.check_returncode()
    data = json.loads(r.stdout)
    with out.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(json.dumps(dict(files=len(data['files']), configs=len(data['configs']),
                          efi_free=data['efi_free'], home_free=data['home_free'], boot_id=data['boot_id'])))

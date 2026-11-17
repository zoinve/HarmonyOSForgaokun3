"""Archive one obsolete, unreferenced commercial initrd, never a shared parent."""
from pathlib import Path
import json
import runpy
import subprocess
import sys

b = Path(__file__).resolve().parent
apply = sys.argv[1:] == ['--apply']
assert sys.argv[1:] in [[], ['--apply']]
runpy.run_path(str(b / 'commercial-workflow-075.py'))['configure_local_transport']()
payload = r'''
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
esp=Path('/boot/efi')
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/efi-unreferenced-cleanup-002')
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
def command(args):return subprocess.check_output(args,text=True,timeout=30)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def new(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def configs():
 return {str(p.relative_to(esp)):p.read_text(errors='replace') for p in esp.rglob('*')
   if p.is_file() and p.suffix.lower() in ['.conf','.cfg','.nsh','.lst','.txt']}
def guard():
 status=command(['bootctl','status','--no-pager'])
 assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
 assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='enabled'
 assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='active'
 assert command(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
 assert command(['findmnt','-n','-o','PARTUUID','--target',str(esp)]).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
 return status
status=guard();config=configs();text='\n'.join(config.values()).replace('\\','/').casefold()
files={str(p.relative_to(esp)):p for p in esp.rglob('*') if p.is_file()}
candidates=[]
for name,path in files.items():
 match=re.fullmatch(r'commercial61-native-(\d{3})/initrd.img',name)
 if not match or not 18<=int(match[1])<=71:continue
 folder=name.split('/')[0]
 if ('/'+folder+'/').casefold() in text:continue
 if path.is_symlink() or not 8*1024**2<=path.stat().st_size<=128*1024**2:continue
 candidates.append(name)
assert candidates,'No bounded, unreferenced obsolete commercial initrd to archive'
selected=min(candidates,key=lambda name:files[name].stat().st_size)
before_free=shutil.disk_usage(esp).free
plan=dict(selected=selected,bytes=files[selected].stat().st_size,sha256=sha(files[selected]),
 efi_free_before=before_free,archive=str(archive),all_referenced_directories_excluded=True,
 all_boot_configs_retained=True,shared_payloads_removed=False,apply=apply)
if apply:
 assert all(plan[key]==expected[key] for key in ['selected','bytes','sha256','archive'])
 assert not archive.exists() and shutil.disk_usage(archive.parent).free>plan['bytes']+1024**3
 before={name:sha(path) for name,path in files.items()}
 firmware=command(['efibootmgr','-v'])
 new(archive/'before.json',json.dumps(dict(plan=plan,efi_hashes=before,configs=config,firmware=firmware,status=status),indent=2).encode())
 backup=archive/'files'/selected
 backup.parent.mkdir(parents=True,exist_ok=True)
 with files[selected].open('rb') as source,backup.open('xb') as dest:
  shutil.copyfileobj(source,dest);dest.flush();os.fsync(dest.fileno())
 assert sha(backup)==plan['sha256']
 os.sync();guard();assert configs()==config and command(['efibootmgr','-v'])==firmware
 assert sha(files[selected])==sha(backup)==before[selected]
 new(archive/'backup-verified.json',json.dumps({selected:before[selected]}).encode())
 files[selected].unlink();os.sync()
 guard();assert configs()==config and command(['efibootmgr','-v'])==firmware
 for name,digest in before.items():
  if name==selected:assert not (esp/name).exists() and sha(backup)==digest
  else:assert sha(esp/name)==digest,name
 plan.update(efi_free_after=shutil.disk_usage(esp).free,backup_hash_verified=True,
  other_efi_files_unchanged=len(before)-1,firmware_unchanged=True,screenoff_enabled_active=True)
 assert plan['efi_free_after']>before_free+8*1024**2
 new(archive/'result.json',json.dumps(plan,indent=2).encode())
print(json.dumps(plan,indent=2))
'''
report = b.parent / 'reports/efi-unreferenced-cleanup-002'
report.mkdir(exist_ok=True)
name = 'cleanup' if apply else 'plan'
assert not (report / (name + '.json')).exists()
expected = json.loads((report / 'plan.json').read_text()) if apply else {}
r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
    '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128', '-o', 'ConnectTimeout=10',
    'matebook', 'sudo -n python3 -'], input='apply=' + repr(apply) + '\nexpected=' + repr(expected) + '\n' + payload,
    text=True, capture_output=True, timeout=180)
for suffix, body in [('stdout', r.stdout), ('stderr', r.stderr)]:
    (report / (name + '.' + suffix)).open('x').write(body)
assert r.returncode == 0, r.stderr
data = json.loads(r.stdout)
(report / (name + '.json')).open('x').write(json.dumps(data, indent=2))
print(r.stdout)

"""Remove exactly completed Harmony trial001..010 entries, not payloads or Ubuntu entries."""
from pathlib import Path
import json,subprocess,sys
base=Path(__file__).resolve().parent.parent
jobs=[]
for n in range(1,11):
 root=base/f'reports/native-original-graphics-boot-{n:03}'
 installed=json.loads((root/'install-result.json').read_text())
 completed=json.loads((root/'runtime-result.json').read_text())
 assert completed['original_images_verified_unchanged']==3 and completed['screen_off_timer']=='active'
 jobs.append(dict(name=f'native-original-graphics-{n:03}+0-1.conf',text=installed['entry_text']))
payload=r'''
from pathlib import Path
import hashlib,json,os,subprocess
esp=Path('/boot/efi');entries=esp/'loader/entries'
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
status=cmd(['bootctl','status','--no-pager'])
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Default Entry: '+default in status and 'Current Entry: '+default in status
assert 'OneShot Entry:' not in status and 'One-shot Entry:' not in status
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=cmd(['efibootmgr','-v'])
for row in jobs:
 p=entries/row['name']
 assert p.is_file() and not p.is_symlink() and p.read_text()==row['text'],row['name']
assert (entries/'native-original-graphics-011+0-1.conf').is_file()
report=dict(deleted_entries=[str(entries/r['name']) for r in jobs],entry_contents=jobs,other_efi_files_unchanged=len(before)-len(jobs),ubuntu_default_unchanged=True,current_candidate_retained='native-original-graphics-011+0-1.conf',boot_payloads_deleted=False,applied=apply)
if apply:
 journal=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/completed-boot-entry-cleanup-001.json')
 with journal.open('x') as f:json.dump(dict(before=before,planned=report),f,indent=2);f.flush();os.fsync(f.fileno())
 for row in jobs:(entries/row['name']).unlink()
 os.sync()
 removed={'loader/entries/'+r['name'] for r in jobs}
 assert all(not (esp/rel).exists() for rel in removed)
 for rel,h in before.items():
  if rel not in removed:assert sha(esp/rel)==h,rel
 assert cmd(['efibootmgr','-v'])==firmware
 assert 'Default Entry: '+default in cmd(['bootctl','status','--no-pager'])
report['bootctl_list']=cmd(['bootctl','list','--no-pager'])
print(json.dumps(report,indent=2))
'''
if __name__=='__main__':
 apply='--apply' in sys.argv
 result=base/'reports/completed-boot-entry-cleanup-001.json'
 if apply:assert not result.exists()
 r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input='jobs='+repr(jobs)+'\napply='+repr(apply)+'\n'+payload,text=True,capture_output=True,timeout=120)
 if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
 data=json.loads(r.stdout)
 if apply:
  with result.open('x') as f:json.dump(data,f,indent=2)
 print(json.dumps({k:v for k,v in data.items() if k not in ['entry_contents','bootctl_list']},indent=2))

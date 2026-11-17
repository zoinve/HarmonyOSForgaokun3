"""Keep two newest commercial diagnostics, standard Ubuntu and original manual entry."""
from pathlib import Path
import json,subprocess
base=Path(__file__).resolve().parents[1]
code=r'''
from pathlib import Path
import base64,datetime,hashlib,json,os,re,subprocess
esp=Path('/boot/efi');entries=esp/'loader/entries'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='enabled'
assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='active'
files=list(entries.glob('*.conf'))
commercial=sorted((p for p in files if re.fullmatch(r'commercial61-native-\d{3}\.conf',p.name)),key=lambda p:int(p.stem.rsplit('-',1)[1]))
assert len(commercial)>=2
keep={default,'harmonyos-gpu-manual.conf',*(p.name for p in commercial[-2:])}
assert all((entries/n).is_file() for n in keep)
remove=[p for p in files if p.name not in keep]
# The inventory's remaining files are historical experimental kernels/tools.
assert all(re.fullmatch(r'commercial61-native-\d{3}\.conf',p.name) or p.name.startswith('ego-') or p.name in ['gk3boot-tools.conf','8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3-el2+.conf'] for p in remove),[p.name for p in remove]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')/('boot-entry-retention-'+stamp)
archive.mkdir(mode=0o700)
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=subprocess.check_output(['efibootmgr','-v'],text=True)
records=[]
for p in remove:
 data=p.read_bytes();dest=archive/p.name
 with dest.open('xb') as out:out.write(data);out.flush();os.fsync(out.fileno())
 assert sha(dest)==sha(p)
 records.append(dict(name=p.name,sha256=sha(p),bytes=len(data),original_base64=base64.b64encode(data).decode()))
manifest=dict(stamp=stamp,archive=str(archive),kept=sorted(keep),removed=records,firmware_before=firmware,ubuntu_default=default,images_and_shared_payloads_removed=False)
with (archive/'before.json').open('x') as out:json.dump(manifest,out,indent=2);out.flush();os.fsync(out.fileno())
for p in remove:
 expected=next(r['sha256'] for r in records if r['name']==p.name)
 assert sha(p)==expected
 p.unlink()
os.sync()
removed={str(p.relative_to(esp)) for p in remove}
assert all((esp/n).is_file() and sha(esp/n)==h for n,h in before.items() if n not in removed)
assert {p.name for p in entries.glob('*.conf')}==keep
assert subprocess.check_output(['efibootmgr','-v'],text=True)==firmware
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
manifest.update(removed_count=len(records),other_efi_files_unchanged=len(before)-len(removed),default_and_firmware_unchanged=True)
with (archive/'result.json').open('x') as out:json.dump(manifest,out,indent=2)
print(json.dumps(manifest))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','-o','ConnectTimeout=10','matebook','sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=120)
assert r.returncode==0,r.stderr
result=json.loads(r.stdout)
folder=base/'reports'/('boot-entry-retention-'+result['stamp']);folder.mkdir()
with (folder/'result.json').open('x') as out:json.dump(result,out,indent=2)
print(json.dumps({k:result[k] for k in ['stamp','archive','kept','removed_count','other_efi_files_unchanged','default_and_firmware_unchanged','images_and_shared_payloads_removed']},indent=2))

"""Record precise preservation differences without exporting firmware device strings."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-175-compile-fix-1'
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,re,subprocess
esp=Path('/boot/efi')
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-175')
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(text):return hashlib.sha256(text.encode()).hexdigest() if text is not None else None
j=json.loads((work/'installation-journal.json').read_text())
changed=[name for name,value in j['efi_before'].items() if not (esp/name).is_file() or sha(esp/name)!=value]
authorized={}
for archive in work.parent.glob('boot-entry-retention-*'):
 path=archive/'result.json'
 if path.is_file():
  for row in json.loads(path.read_text())['removed']:authorized['loader/entries/'+row['name']]=row['sha256']
removed=[name for name in changed if name in authorized and authorized[name]==j['efi_before'][name] and not (esp/name).exists()]
assert set(changed)<={'loader/random-seed',*removed},changed
current=subprocess.check_output(['efibootmgr','-v'],text=True)
def rows(text):
 result={}
 for line in text.splitlines():
  key=line.split(':',1)[0]
  entry=re.match(r'^(Boot[0-9A-Fa-f]{4})\*?',line)
  if entry:key=entry[1]
  assert key not in result
  result[key]=line
 return result
before,after=rows(j['firmware']),rows(current)
differences=[]
for key in sorted(set(before)|set(after)):
 if before.get(key)==after.get(key):continue
 row=dict(field=key,previous_sha256=digest(before.get(key)),current_sha256=digest(after.get(key)),
  previous_present=key in before,current_present=key in after)
 if key in ['BootCurrent','BootOrder','Timeout']:
  for label,values in [('previous',before),('current',after)]:
   value=values.get(key,'').partition(':')[2].strip()
   if re.fullmatch(r'[0-9A-Fa-f, ]+(?: seconds)?',value):row[label]=value
 row['current_usb_device_path_seen']='USB' in after.get(key,'')
 differences.append(row)
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Default Entry: '+default in status and 'Current Entry: '+default in status and 'OneShot Entry:' not in status
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
verified={}
for name in ['system.img','vendor.img','sysprod.img','chipprod.img']:
 path=work.parent/'commercial61-original-001'/name
 expected=json.loads(path.with_name(name+'.json').read_text())['sha256']
 verified[name]=sha(path)
 assert expected==verified[name]
installed=json.loads((work/'installation-result.json').read_text())
assert sha(esp/'usb175.img')==installed['initrd_sha256']==sha(esp/'commercial61-native-175/initrd.img')
timers={operation:subprocess.run(['systemctl',operation,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip() for operation in ['is-enabled','is-active']}
assert timers=={'is-enabled':'enabled','is-active':'active'}
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 ubuntu_current_and_default=True,prior_efi_files_unchanged=len(j['efi_before'])-len(changed),
 boot_managed_changes=[name for name in changed if name not in removed],user_authorized_old_entries_removed=removed,
 firmware_unchanged=not differences,firmware_differences=differences,
 commercial_original_images_unchanged=verified,lab_partition_unmounted=True,
 custom_screenoff_timer_enabled_active=True,old_manual_entry_retained=(esp/'loader/entries/harmonyos-gpu-manual.conf').is_file(),
 short_alias_and_original_payload_hashes_verified=True,raw_firmware_strings_exported=False),indent=2))
'''


if __name__ == '__main__':
    output=REPORT/'preservation-difference-inspection.json'
    assert not output.exists()
    runpy.run_path(str(BASE/'commercial-workflow-175.py'))['configure_local_transport']()
    proc=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],
        input=PAYLOAD,text=True,capture_output=True,timeout=240)
    (REPORT/'preservation-difference-inspection.stderr').open('x').write(proc.stderr)
    assert proc.returncode==0,proc.stderr
    data=json.loads(proc.stdout)
    output.open('x').write(json.dumps(data,indent=2))
    print(json.dumps(data,indent=2))

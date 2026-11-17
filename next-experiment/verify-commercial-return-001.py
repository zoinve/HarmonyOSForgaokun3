"""Read-only post-return preservation and commercial-image hash verification."""
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-001'
assert json.loads((root/'boot-observation.json').read_text())['returned']
code=r'''
from pathlib import Path
import hashlib,json,subprocess
esp=Path('/boot/efi');work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-001')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((work/'installation-journal.json').read_text())
changed=[n for n,h in j['efi_before'].items() if not (esp/n).is_file() or sha(esp/n)!=h]
assert set(changed)<= {'loader/random-seed'},changed
assert subprocess.check_output(['efibootmgr','-v'],text=True)==j['firmware']
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='disabled'
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
images=work.parent/'commercial61-original-001';verified={}
for name in ['system.img','vendor.img','sysprod.img','chipprod.img']:
 expected=json.loads((images/(name+'.json')).read_text())['sha256'];actual=sha(images/name)
 assert expected==actual,name
 verified[name]=actual
assert sha(esp/'commercial61-native-001/initrd.img')==json.loads((work/'installation-result.json').read_text())['initrd_sha256']
assert (esp/'loader/entries/harmonyos-gpu-manual.conf').is_file()
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),ubuntu_current_and_default=True,
 prior_efi_files_unchanged=len(j['efi_before'])-len(changed),boot_managed_changes=changed,
 firmware_unchanged=True,commercial_original_images_unchanged=verified,lab_partition_unmounted=True,
 custom_screenoff_timer_disabled=True,old_manual_entry_retained=True)))
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=400)
assert r.returncode==0,r.stderr
(root/'post-return-verification.json').open('x').write(r.stdout);print(r.stdout)

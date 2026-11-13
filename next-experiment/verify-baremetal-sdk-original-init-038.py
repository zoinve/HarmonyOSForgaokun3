"""Independent read-only verification of trial 038, preserving failures as failures."""
import subprocess

payload=r'''
from pathlib import Path
import hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-sdk-original-init-qemu-038')
work=root/local.name;out=local/'independent-verification.json';assert not out.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((local/'result.json').read_text());assert r==json.loads((work/'result.json').read_text())
s=(local/'serial.log').read_bytes();assert s==(work/'serial.log').read_bytes()
assert hashlib.sha256(s).hexdigest()==r['serial_sha256'] and len(s)==r['serial_bytes']
p=json.loads((root/'baremetal-sdk-original-init-038/result.json').read_text())
for row in p['files'].values():
 f=Path(row['path']);assert f.stat().st_size==row['bytes'] and sha(f)==row['sha256']
assert sha(root/'baremetal-sdk-original-init-038/init.c')==p['source_sha256']
for row in r['original_images'].values():
 f=Path(row['path']);assert f.stat().st_size==row['bytes'] and sha(f)==row['sha256']
c=r['command'];assert sha(Path(c[c.index('-kernel')+1]))=='5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d'
assert c[c.index('-nic')+1]=='none'
args=c[c.index('-append')+1].split();assert 'enforcing=1' in args and 'ohos.boot.hardware=hmos.emulator' in args
assert 'lsm=landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,bpf' in args
drives=[c[i+1] for i,v in enumerate(c) if v=='-drive'];assert len(drives)==4
assert 'readonly=on' not in drives[0] and all('readonly=on' in d for d in drives[1:])
devices=[c[i+1] for i,v in enumerate(c) if v=='-device']
assert devices==['virtio-blk-device,drive=sdkdata,serial=sdk-testdata',
 'virtio-blk-device,drive=sdkro0,serial=sdk-sysprod',
 'virtio-blk-device,drive=sdkro1,serial=sdk-vendor',
 'virtio-blk-device,drive=sdkro2,serial=sdk-system']
assert r['original_fstab_and_hardware_guard_observed']==(b'ORIGINAL_INIT038_LAYOUT_GUARDED' in s)
for key in ['original_images_unchanged','kernel_and_config_unchanged','native_config_unchanged','source_critical_unchanged']:assert r[key]
f=Path(r['scratch_data']['retained_path']);assert f.stat().st_size==536870912 and sha(f)==r['scratch_data']['after_sha256']
assert not r['scratch_data']['original_userdata_attached']
assert not r['runtime_verified'] and not r['services_ready'] and b'Kernel panic' not in s
d=dict(serial_sha256=sha(local/'serial.log'),local_wsl_result_serial_identical=True,
 prepared_files_and_source_verified=True,all_original_images_verified_unchanged=True,
 kernel_verified=True,preservation_flags_confirmed=True,private_scratch_image_verified=True,
 hardware_and_readonly_drive_contract_verified=True,
 fstab_runtime_guard_observed=r['original_fstab_and_hardware_guard_observed'],
 service_readiness_not_claimed=True,samgr_registration_log_count=s.count(b'SAMGR: insert SA:'),
 original_samgr_main_observed=b'SAMGR: main called' in s,
 token_lock_failure_log_count=s.count(b'LockNativeTokenFile'),
 token_initialization_failure_log_count=s.count(b'get tokenid failed'))
out.write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
'''
compile(payload,'verify-original-init-038','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

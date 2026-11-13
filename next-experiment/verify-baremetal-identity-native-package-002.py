"""Independently compare packaged bytes to the native build, not the QEMU storage build."""
import subprocess

payload=r'''
from pathlib import Path
import gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883')
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-native-package-002')
work=root/local.name;out=local/'independent-verification.json';assert not out.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
d=json.loads((local/'result.json').read_text());assert d==json.loads((work/'result.json').read_text())
p=json.loads((root/'baremetal-identity-profile-003/result.json').read_text())
archive=Path(d['archive']);assert archive.stat().st_size==d['archive_bytes'] and sha(archive)==d['archive_sha256']
raw=gzip.decompress(archive.read_bytes());entries={};pos=0
while True:
 h=raw[pos:pos+110];assert len(h)==110 and h[:6]==b'070701'
 size=int(h[54:62],16);ns=int(h[94:102],16);name=raw[pos+110:pos+109+ns].decode();start=(pos+110+ns+3)&~3;pos=(start+size+3)&~3
 if name=='TRAILER!!!':break
 assert name not in entries and not name.startswith('/') and '..' not in Path(name).parts
 assert start+size<=len(raw);entries[name]=raw[start:start+size]
assert 'init' not in entries and len(entries)==620
prefix='lib/modules/7.1.0-rc3-gaokun3-el2/kernel/'
assert {n for n in entries if n.endswith('.ko')}=={prefix+r['path'] for r in p['module_inventory']}
for row in p['module_inventory']:
 data=entries[prefix+row['path']];assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert len(p['module_inventory'])==391
assert sha(work/'linux')==d['kernel_sha256']==p['artifacts'][0]['sha256']=='4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166'
assert (work/'linux').stat().st_size==p['artifacts'][0]['bytes']
assert sha(work/'sc8280xp-huawei-gaokun3.dtb')==d['dtb_sha256']==p['artifacts'][1]['sha256']
assert sha(root/'baremetal-identity-profile-003/out/.config')==p['native_config_sha256']==d['profile_config_sha256']
config=(root/'baremetal-identity-profile-003/out/.config').read_text()
assert '# CONFIG_ANDROID_BINDERFS is not set' in config and 'CONFIG_ACCESS_TOKENID=y' in config
assert 'CONFIG_LSM="landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,bpf"' in config
assert '# CONFIG_VIRTIO_MENU is not set' in config
result=dict(local_wsl_result_equal=True,archive_bytes_and_sha256_verified=True,
 all_391_packaged_module_bytes_match_native_profile=True,native_kernel_and_dtb_verified=True,
 native_config_verified=True,no_test_only_virtio_profile=True,contains_init=False,
 installed=False,boot_entries_modified=False,native_boot_attempted=False,runtime_verified=False)
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
'''
compile(payload,'verify-native-package-002','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=90)
    raise SystemExit(r.returncode)

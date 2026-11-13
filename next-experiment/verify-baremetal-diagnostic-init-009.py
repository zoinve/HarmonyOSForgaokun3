"""Independently compare actual archive records and unchanged base before board staging."""
import subprocess

payload=r'''
from pathlib import Path
import gzip,hashlib,json,stat
root=Path('/home/zoinve/harmony-virgl-883');project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
out=project/'reports/baremetal-diagnostic-init-009/independent-verification.json';assert not out.exists()
meta=json.loads((project/'reports/baremetal-diagnostic-init-009/result.json').read_text())
base=json.loads((project/'reports/baremetal-identity-native-package-002/result.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def archive(p):
    raw=gzip.decompress(p.read_bytes());entries={};pos=0
    while True:
        h=raw[pos:pos+110];assert h[:6]==b'070701'
        mode=int(h[14:22],16);uid=int(h[22:30],16);gid=int(h[30:38],16);size=int(h[54:62],16);ns=int(h[94:102],16)
        name=raw[pos+110:pos+109+ns].decode();start=(pos+110+ns+3)&~3;pos=(start+size+3)&~3
        assert start+size<=len(raw)
        if name=='TRAILER!!!':break
        name=name.removeprefix('./');assert name not in entries
        entries[name]=(mode,uid,gid,raw[start:start+size])
    return entries
p=Path(meta['archive']);assert p.stat().st_size==meta['archive_bytes'] and sha(p)==meta['archive_sha256']
parent=root/'baremetal-identity-native-package-002/diagnostic-base.cpio.gz'
assert sha(parent)==base['archive_sha256']
old=archive(parent);new=archive(p);assert set(new)-set(old)=={'init','bin/native-identity-read-002'} and set(old)<=set(new)
for name,record in old.items():assert new[name]==record,name
for name,path,key in [('init',p.parent/'init','binary_sha256'),('bin/native-identity-read-002',root/'baremetal-native-identity-qemu-047/probe','helper_sha256')]:
    assert new[name][3]==path.read_bytes() and sha(path)==meta[key] and stat.S_ISREG(new[name][0]) and new[name][0]&0o111
for name,key in [('linux','kernel_sha256'),('sc8280xp-huawei-gaokun3.dtb','dtb_sha256')]:assert sha(parent.parent/name)==meta[key]
qemu=json.loads((project/'reports/baremetal-native-identity-qemu-047/independent-verification.json').read_text())
assert qemu['positive_legacy_binder_and_enforcing_verified'] and qemu['missing_opt_in_refused']
assert json.loads((p.parent/'result.json').read_text())==meta
result=dict(archive_sha256=meta['archive_sha256'],archive_bytes=p.stat().st_size,all_parent_records_bytes_modes_uid_gid_preserved=True,parent_records=len(old),added_records=sorted(set(new)-set(old)),binary_helper_kernel_dtb_hashes_verified=True,independent_qemu_helper_checks_verified=True,local_wsl_manifest_equal=True,board_boot_attempted=False,boot_entry_installed=False)
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
'''
compile(payload,'independent-native-diag009','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=90)
    raise SystemExit(r.returncode)

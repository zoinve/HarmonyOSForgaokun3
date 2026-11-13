"""Compile isolated PID1 probe and extract unmodified vendor production policy read-only."""
from pathlib import Path
import subprocess

payload='source='+repr(Path(__file__).with_name('baremetal-selinux-load-013.c').read_text())+'\n'+r'''
from pathlib import Path
import hashlib,json,subprocess,struct
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-selinux-load-013'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-selinux-load-013')
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(image,path,name):
 p=work/name;r=subprocess.run(['debugfs','-R','dump '+path+' '+str(p),'/mnt/d/Download/pc_all_arm/'+image],text=True,capture_output=True,timeout=30)
 (local/(name+'.extraction.txt')).write_text(r.stdout+r.stderr)
 assert r.returncode==0 and p.exists() and p.stat().st_size>0,(image,path,r.stderr)
 return p
policy=dump('vendor.img','/etc/selinux/prebuild_sepolicy/policy.31','policy.31')
system_hash=dump('system.img','/system/etc/selinux/system.cil.sha256','system.cil.sha256')
vendor_hash=dump('vendor.img','/etc/selinux/prebuild_sepolicy.system.cil.sha256','prebuild.system.cil.sha256')
assert system_hash.read_bytes()==vendor_hash.read_bytes(),'Original prebuilt/system policy fingerprints differ'
data=policy.read_bytes();assert struct.unpack_from('<I',data)[0]==0xf97cff8c
length=struct.unpack_from('<I',data,4)[0];assert length<64
version=struct.unpack_from('<I',data,8+length)[0];assert version==31,version
(work/'init.c').write_text(source)
r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/'init.c'),'-o',str(work/'init')],text=True,capture_output=True,timeout=60)
(local/'compile.stdout').write_text(r.stdout);(local/'compile.stderr').write_text(r.stderr);assert r.returncode==0,r.stderr
elf=subprocess.check_output(['readelf','-h',str(work/'init')],text=True);assert 'AArch64' in elf
files={p.name:dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in [work/'init',policy]}
report=dict(path=str(work/'init'),bytes=files['init']['bytes'],sha256=files['init']['sha256'],source_sha256=sha(work/'init.c'),files=files,
 policy_version=version,original_system_vendor_fingerprints_equal=True,policy_source='vendor.img:/etc/selinux/prebuild_sepolicy/policy.31',
 original_policy_modified=False,runtime_verified=False,services_tested=False,reboot_requested=False)
(work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
'''
compile(payload,'selinux-013-preparation','exec')
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
 raise SystemExit(r.returncode)

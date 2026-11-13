"""Add read-only image-test transport to an isolated console kernel, never to the board profile."""
import subprocess

payload=r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');parent=root/'baremetal-identity-profile-003'
work=root/'baremetal-sdk-storage-test-004';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-sdk-storage-test-004')
assert not work.exists() and not local.exists()
assert shutil.disk_usage(root).free>6*1024**3
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prior=json.loads((parent/'result.json').read_text());assert prior['compiled']
assert sha(parent/'test-out/.config')==prior['test_config_sha256']
assert sha(parent/'out/.config')==prior['native_config_sha256']
assert sha(Path(prior['test_kernel']['path']))==prior['test_kernel']['sha256']
identity=json.loads((root/'baremetal-identity-candidate-002/result.json').read_text())
critical=identity['patched_critical_hashes'];drivers=identity['driver_hashes']
for n,d in critical.items():assert sha(parent/'linux'/n)==d,n
for n,d in drivers.items():assert sha(parent/'linux/drivers/accesstokenid'/n)==d,n
work.mkdir();local.mkdir();src=work/'linux';build=work/'out';build.mkdir()
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-',PYTHONDONTWRITEBYTECODE='1')
start=time.monotonic();report=dict(compiled=False,test_only=True,installed=False,reboot_requested=False,boot_entries_modified=False,images_attached=False)
def run(args,name,timeout=300):
 with (work/name).open('xb') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert r.returncode==0,name+' failed; preserve all numbered outputs'
def config(path):
 d={}
 for l in path.read_text().splitlines():
  if l.startswith('CONFIG_'):
   k,v=l.split('=',1);d[k]=v
  elif l.startswith('# CONFIG_') and l.endswith(' is not set'):d[l[2:-11]]='n'
 return d
try:
 run(['cp','-a','--reflink=auto',str(parent/'linux'),str(src)],'copy-source.log')
 shutil.copyfile(parent/'test-out/.config',build/'.config')
 run([str(src/'scripts/config'),'--file',str(build/'.config'),'--enable','VIRTIO_MENU','--enable','VIRTIO_MMIO','--enable','VIRTIO_BLK','--disable','VIRTIO_PCI','--disable','VIRTIO_MMIO_CMDLINE_DEVICES'],'select.log')
 common=['make','-C',str(src),'O='+str(build)]
 run(common+['olddefconfig'],'configure.log')
 before=config(parent/'test-out/.config');after=config(build/'.config')
 changes={k:dict(before=before.get(k,'n'),after=after.get(k,'n')) for k in before.keys()|after.keys() if before.get(k,'n')!=after.get(k,'n')}
 assert {'CONFIG_VIRTIO_MENU','CONFIG_VIRTIO_MMIO','CONFIG_VIRTIO_BLK'}<=changes.keys(),changes
 assert set(changes)<= {'CONFIG_VIRTIO_MENU','CONFIG_VIRTIO_MMIO','CONFIG_VIRTIO_BLK','CONFIG_SG_POOL'},changes
 assert all(v==dict(before='n',after='y') for v in changes.values()),changes
 for k in ['CONFIG_LSM','CONFIG_ANDROID_BINDERFS','CONFIG_ANDROID_BINDER_IPC','CONFIG_ANDROID_BINDER_DEVICES','CONFIG_SECURITY_SELINUX','CONFIG_SECURITY_SELINUX_DEVELOP','CONFIG_SECCOMP','CONFIG_QCOM_WDT','CONFIG_ACCESS_TOKENID','CONFIG_ARM64_4K_PAGES']:
  assert after.get(k)==before.get(k),(k,before.get(k),after.get(k))
 assert after['CONFIG_EXT4_FS']=='y' and after['CONFIG_SERIAL_AMBA_PL011_CONSOLE']=='y'
 report['test_only_config_changes']=changes
 shutil.copyfile(build/'.config',local/'resolved.config')
 run(common+['-j4','Image'],'build.log',7200)
 p=build/'arch/arm64/boot/Image';report['test_kernel']=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
 report['test_config_sha256']=sha(build/'.config');report['compiled']=True
finally:
 report.update(elapsed_seconds=time.monotonic()-start,parent_test_config_unchanged=sha(parent/'test-out/.config')==prior['test_config_sha256'],
 parent_native_config_unchanged=sha(parent/'out/.config')==prior['native_config_sha256'],
 parent_test_kernel_unchanged=sha(Path(prior['test_kernel']['path']))==prior['test_kernel']['sha256'],
 parent_source_critical_unchanged=all(sha(parent/'linux'/n)==d for n,d in critical.items()),
 source_critical_unchanged=src.exists() and all(sha(src/n)==d for n,d in critical.items()),
 driver_unchanged=src.exists() and all(sha(src/'drivers/accesstokenid'/n)==d for n,d in drivers.items()))
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
'''
compile(payload,'sdk-storage-test-004-build','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=7800)
    raise SystemExit(r.returncode)

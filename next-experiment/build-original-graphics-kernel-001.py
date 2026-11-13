"""Separate QEMU virtio graphics kernel; never install or change the board profile."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883')
parent=root/'baremetal-sdk-storage-test-004'
identity=root/'baremetal-identity-profile-003'
work=root/'original-graphics-kernel-001'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/original-graphics-kernel-001')
assert not work.exists() and not local.exists()
assert shutil.disk_usage(root).free>8*1024**3
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prior=json.loads((parent/'result.json').read_text())
native=json.loads((identity/'result.json').read_text())
assert prior['compiled'] and prior['test_only']
assert sha(parent/'out/.config')==prior['test_config_sha256']
assert sha(Path(prior['test_kernel']['path']))==prior['test_kernel']['sha256']
assert sha(identity/'out/.config')==native['native_config_sha256']
critical=['include/linux/sched.h','include/uapi/linux/android/binder.h','drivers/android/binder.c','drivers/android/binder_internal.h','drivers/accesstokenid/access_tokenid.c','drivers/accesstokenid/access_tokenid.h']
source_before={n:sha(parent/'linux'/n) for n in critical}
work.mkdir();local.mkdir();build=work/'out';build.mkdir()
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-',PYTHONDONTWRITEBYTECODE='1')
report=dict(compiled=False,test_only=True,physical_board_test=False,installed=False,reboot_requested=False,boot_entries_modified=False)
start=time.monotonic()
def run(args,name,timeout=300):
 with (work/name).open('xb') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert r.returncode==0,name+' failed; numbered outputs retained'
def config(path):
 d={}
 for line in path.read_text().splitlines():
  if line.startswith('CONFIG_'):
   k,v=line.split('=',1);d[k]=v
  elif line.startswith('# CONFIG_') and line.endswith(' is not set'):d[line[2:-11]]='n'
 return d
src=work/'linux'
try:
 run(['cp','-a','--reflink=auto',str(parent/'linux'),str(src)],'copy-source.log')
 shutil.copyfile(parent/'out/.config',build/'.config')
 selected=['DRM','DRM_VIRTIO_GPU','OVERLAY_FS']
 args=[str(src/'scripts/config'),'--file',str(build/'.config')]
 for name in selected:args+=['--enable',name]
 run(args,'select.log')
 common=['make','-C',str(src),'O='+str(build)]
 run(common+['olddefconfig'],'configure.log')
 before=config(parent/'out/.config');after=config(build/'.config')
 changes={k:dict(before=before.get(k,'n'),after=after.get(k,'n')) for k in before.keys()|after.keys() if before.get(k,'n')!=after.get(k,'n')}
 for k in ['CONFIG_LSM','CONFIG_ANDROID_BINDERFS','CONFIG_ANDROID_BINDER_IPC','CONFIG_ANDROID_BINDER_DEVICES','CONFIG_SECURITY_SELINUX','CONFIG_SECURITY_SELINUX_DEVELOP','CONFIG_SECCOMP','CONFIG_QCOM_WDT','CONFIG_ACCESS_TOKENID','CONFIG_ARM64_4K_PAGES','CONFIG_VIRTIO_BLK']:
  assert after.get(k)==before.get(k),(k,before.get(k),after.get(k))
 assert all(after['CONFIG_'+name]=='y' for name in selected)
 # Selection may promote DRM dependencies from module to built-in, but may not
 # remove an existing capability or modify a non-graphics configuration family.
 prefixes=('CONFIG_DRM','CONFIG_DMA','CONFIG_FB','CONFIG_FRAMEBUFFER','CONFIG_GENERIC_ALLOCATOR','CONFIG_OVERLAY_FS','CONFIG_SYNC_FILE','CONFIG_INTERVAL_TREE','CONFIG_HDMI','CONFIG_CEC','CONFIG_I2C','CONFIG_VIDEO','CONFIG_BACKLIGHT','CONFIG_VIRTIO_DMA_SHARED_BUFFER','CONFIG_TTM','CONFIG_DMEM')
 assert all(k.startswith(prefixes) and v['after']!='n' for k,v in changes.items()),changes
 report['test_only_config_changes']=changes
 shutil.copyfile(build/'.config',local/'resolved.config')
 run(common+['-j4','Image'],'build.log',7200)
 image=build/'arch/arm64/boot/Image'
 report.update(compiled=True,test_kernel=dict(path=str(image),bytes=image.stat().st_size,sha256=sha(image)),test_config_sha256=sha(build/'.config'))
finally:
 report.update(elapsed_seconds=time.monotonic()-start,
  parent_kernel_unchanged=sha(Path(prior['test_kernel']['path']))==prior['test_kernel']['sha256'],
  parent_config_unchanged=sha(parent/'out/.config')==prior['test_config_sha256'],
  native_config_unchanged=sha(identity/'out/.config')==native['native_config_sha256'],
  source_critical_unchanged=all(sha(parent/'linux'/n)==h for n,h in source_before.items()))
 for dest in [work/'result.json',local/'result.json']:
  with dest.open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report,indent=2),flush=True)
'''
compile(payload, 'original-graphics-kernel-001', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=7800)
    raise SystemExit(result.returncode)

"""Bounded original PID1 observation. Never classify mere execution as service readiness."""
from pathlib import Path
import subprocess

payload=r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');name='baremetal-sdk-original-init-qemu-034'
work=root/name;local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports')/name
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prep=json.loads((root/'baremetal-sdk-original-init-034/result.json').read_text())
for row in prep['files'].values():
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert prep['files']['policy.31']['sha256']=='3119d6aae760a6d692459ce9d83aeb6354301bc1fb9b084d005664f6a543d8e5'
storage=json.loads((root/'baremetal-sdk-storage-test-004/result.json').read_text())
kernel=Path(storage['test_kernel']['path']);config=root/'baremetal-sdk-storage-test-004/out/.config'
assert storage['compiled'] and storage['test_only']
assert sha(kernel)==storage['test_kernel']['sha256']=='5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d'
assert sha(config)==storage['test_config_sha256']
candidate=root/'baremetal-identity-profile-003'
profile=json.loads((candidate/'result.json').read_text())
assert sha(candidate/'out/.config')==profile['native_config_sha256']
critical=['include/linux/sched.h','include/uapi/linux/android/binder.h','drivers/android/binder.c','drivers/android/binder_internal.h','drivers/accesstokenid/access_tokenid.c','drivers/accesstokenid/access_tokenid.h']
source_before={n:sha(candidate/'linux'/n) for n in critical}
images={}
for filename in ['system.img','vendor.img','sys_prod.img']:
 p=Path('/mnt/d/Download/pc_all_arm')/filename
 assert p.is_file() and not p.is_symlink()
 images[filename]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert images['system.img']['sha256']=='19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3'
archive=bytearray();inode=1
def add(name,mode,data=b'',major=0,minor=0):
 global inode
 encoded=name.encode()+b'\0'
 fields=[inode,mode,0,0,1,0,len(data),0,0,major,minor,len(encoded),0];inode+=1
 archive.extend(b'070701'+''.join('%08x'%v for v in fields).encode()+encoded)
 archive.extend(b'\0'*((-len(archive))%4));archive.extend(data);archive.extend(b'\0'*((-len(archive))%4))
for n in ['dev','proc','sys']:add(n,stat.S_IFDIR|0o755)
add('dev/console',stat.S_IFCHR|0o600,major=5,minor=1)
add('init',stat.S_IFREG|0o700,Path(prep['files']['init']['path']).read_bytes())
add('TRAILER!!!',0)
initrd=work/'initramfs.cpio.gz';initrd.write_bytes(gzip.compress(bytes(archive),mtime=0))
cmdline='console=ttyAMA0 rdinit=/init harmony.original_init_test=1 enforcing=1 lsm=landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,bpf panic=-1'
command=['qemu-system-aarch64','-machine','virt,gic-version=3','-cpu','max','-accel','tcg,thread=multi','-smp','2','-m','2048','-nodefaults','-display','none','-monitor','none','-serial','stdio','-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(initrd),'-append',cmdline]
for i,(filename,row) in enumerate(images.items()):
 identity='sdk'+str(i)
 command+=['-drive','file='+row['path']+',if=none,id='+identity+',format=raw,readonly=on','-device','virtio-blk-device,drive='+identity]
report=dict(bounded_observation_complete=False,runtime_verified=False,services_ready=False,
 original_init_handoff_attempted=False,original_init_exec_failure_observed=False,
 production_policy_enforcement_after_handoff_verified=False,physical_board_test=False,
 installed=False,reboot_requested=False,network_attached=False,gpu_attached=False,
 original_images=images,command=command,timeout_seconds=60,initrd_sha256=sha(initrd))
start=time.monotonic();serial=work/'serial.log'
try:
 with serial.open('wb') as f:
  try:
   r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
   report['qemu_returncode']=r.returncode;report['observation_timed_out']=False
  except subprocess.TimeoutExpired:
   report['qemu_returncode']=None;report['observation_timed_out']=True
 report['bounded_observation_complete']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start
 report['original_images_unchanged']=all(Path(row['path']).stat().st_size==row['bytes'] and sha(Path(row['path']))==row['sha256'] for row in images.values())
 report['kernel_and_config_unchanged']=sha(kernel)==storage['test_kernel']['sha256'] and sha(config)==storage['test_config_sha256']
 report['native_config_unchanged']=sha(candidate/'out/.config')==profile['native_config_sha256']
 report['source_critical_unchanged']=all(sha(candidate/'linux'/n)==digest for n,digest in source_before.items())
 if serial.exists():
  data=serial.read_bytes();(local/'serial.log').write_bytes(data)
  report['serial_bytes']=len(data);report['serial_sha256']=hashlib.sha256(data).hexdigest()
  report['original_init_handoff_attempted']=b'ORIGINAL_INIT034_HANDOFF' in data
  report['original_init_exec_failure_observed']=b'ORIGINAL_INIT034_FAIL original init exec' in data
  report['helper_failure_observed']=b'ORIGINAL_INIT034_FAIL' in data
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
assert report['original_images_unchanged'] and report['kernel_and_config_unchanged'] and report['native_config_unchanged'] and report['source_critical_unchanged'],'Preservation failed; report retained'
'''
compile(payload,'original-init-034-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(r.returncode)

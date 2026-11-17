"""Exercise the real ext4 resize ioctl on a private seed copy, never a device image."""
from pathlib import Path
import json,subprocess

prepare=r'''
from pathlib import Path
import ast,hashlib,json,runpy
r=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=r/'commercial-data-010-verification';assert not work.exists();work.mkdir()
tree=ast.parse(runpy.run_path(str(base/'build-native-return-overlay-033.py'))['payload'])
ns={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'<archive-helpers>','exec'),ns)
seed=ns['parse'](r/'commercial61-native-010/initrd.img')['native-target/scratch-data.ext4'][1]
with (work/'fresh-test.ext4').open('xb') as f:f.write(seed);f.truncate(8589934592)
(work/'mount').mkdir()
(work/'seed.json').open('x').write(json.dumps(dict(bytes=len(seed),sha256=hashlib.sha256(seed).hexdigest())))
print('Private seed copy prepared; no original filesystem modified')
'''
exercise=r'''
from pathlib import Path
import fcntl,json,os,struct,subprocess
work=Path('/home/zoinve/harmony-virgl-883/commercial-data-010-verification')
image=work/'fresh-test.ext4';target=work/'mount';loop=None;mounted=False
try:
 loop=subprocess.check_output(['losetup','--find','--show',str(image)],text=True).strip()
 assert loop.startswith('/dev/loop')
 subprocess.run(['mount','-t','ext4','-o','nosuid,nodev,noexec,noatime,data=ordered',loop,str(target)],check=True)
 mounted=True;before=os.statvfs(target)
 assert before.f_frsize==4096 and before.f_blocks*4096<8589934592
 fd=os.open(target,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:fcntl.ioctl(fd,0x40086610,struct.pack('Q',8589934592//4096))
 finally:os.close(fd)
 after=os.statvfs(target);assert after.f_blocks*4096>=7516192768
 result=dict(seed=json.loads((work/'seed.json').read_text()),before_capacity_bytes=before.f_blocks*4096,
  after_capacity_bytes=after.f_blocks*4096,after_available_bytes=after.f_bavail*4096,
  real_ext4_online_resize_ioctl_passed=True,private_mount_namespace=True,
  original_images_modified=False,target_device_tested=False,ram_backed=False)
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True)
 if loop:subprocess.run(['losetup','--detach',loop],check=True)
result['private_mount_and_loop_released']=True
(work/'result.json').open('x').write(json.dumps(result,indent=2));print(json.dumps(result))
'''

if __name__=='__main__':
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=prepare,text=True,check=True,timeout=60)
    run=subprocess.run(['wsl','-d','Debian','-u','root','--','unshare','--mount','--propagation','private','--','python3','-'],input=exercise,text=True,capture_output=True,timeout=120)
    dest=Path(__file__).resolve().parent.parent/'reports/commercial61-native-010'
    (dest/'filesystem-verification.stdout').open('x',encoding='utf-8').write(run.stdout)
    (dest/'filesystem-verification.stderr').open('x',encoding='utf-8').write(run.stderr)
    assert run.returncode==0,run.stderr
    result=json.loads(run.stdout)
    (dest/'filesystem-verification.json').open('x',encoding='utf-8').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

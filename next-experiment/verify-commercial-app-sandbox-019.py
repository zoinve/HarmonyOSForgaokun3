"""Private WSL mount/chroot test; never accesses or boots the target device."""
import subprocess,sys

payload=r'''
from pathlib import Path
import json,runpy,subprocess,hashlib,os
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-app-sandbox-019-verification-r2'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/commercial-app-sandbox-019-verification-r2')
if not work.exists():work.mkdir();local.mkdir()
else:
 assert RESUME and not (work/'result.json').exists() and not (work/'jail').exists()
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
original=json.loads(subprocess.check_output(['debugfs','-R','cat /system/etc/sandbox/appdata-sandbox.json',str(image)],stderr=subprocess.DEVNULL))
new=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/commercial-app-sandbox-019.py')['repair'](original)
for name,value in [('original.json',original),('alias.json',new)]:
 p=work/name;text=json.dumps(value,indent=2)
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
source=work/'source';(source/'seccomp').mkdir(parents=True,exist_ok=True)
f=source/'seccomp/libapp_filter.z.so'
if not f.exists():subprocess.run(['debugfs','-R',f'dump /system/lib64/seccomp/libapp_filter.z.so {f}',str(image)],check=True,capture_output=True)
assert f.read_bytes().startswith(b'\x7fELF')
child=r"""
from pathlib import Path
import os,subprocess,errno,json,hashlib
work=Path(__import__('sys').argv[1]); jail=work/'jail'; a=jail/'system/lib64'; b=jail/'usr/system/lib64'
a.mkdir(parents=True);b.mkdir(parents=True)
def run(*args):subprocess.run(args,check=True,capture_output=True)
try:
 run('mount','--bind',str(work/'source'),str(a));run('mount','-o','remount,bind,ro',str(a))
 assert not (b/'seccomp/libapp_filter.z.so').exists()
 run('mount','--bind',str(a),str(b))
 fa=a/'seccomp/libapp_filter.z.so';fb=b/'seccomp/libapp_filter.z.so'
 assert fa.stat().st_ino==fb.stat().st_ino and fa.stat().st_dev==fb.stat().st_dev
 try:fb.open('ab').close()
 except OSError as e:assert e.errno==errno.EROFS
 else:raise AssertionError('alias became writable')
 pid=os.fork()
 if not pid:
  try:
   os.chroot(jail);os.chdir('/')
   assert Path('/usr/system/lib64/seccomp/libapp_filter.z.so').read_bytes()==Path('/system/lib64/seccomp/libapp_filter.z.so').read_bytes()
   assert not Path('/usr/system/etc').exists()
   os._exit(0)
  except BaseException:os._exit(1)
 assert os.waitpid(pid,0)[1]==0
 print(json.dumps(dict(actual_filter_sha256=hashlib.sha256(fa.read_bytes()).hexdigest(),same_inode=True,read_only_alias=True,chroot_layer_path_read=True,unrelated_system_etc_exposed=False,target_device_accessed=False,seccomp_load_runtime_verified=False,desktop_verified=False)))
finally:
 for p in [b,a]:subprocess.run(['umount',str(p)],capture_output=True)
"""
(work/'mount-test.py').write_text(child)
r=subprocess.run(['unshare','--mount','--propagation','private','python3',str(work/'mount-test.py'),str(work)],capture_output=True,text=True,timeout=45)
for dest in [work,local]:
 suffix='.1' if RESUME else ''
 (dest/('test.stdout'+suffix)).write_text(r.stdout);(dest/('test.stderr'+suffix)).write_text(r.stderr)
assert r.returncode==0,(r.returncode,r.stderr)
result=json.loads(r.stdout)
for dest in [work,local]:(dest/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','-u','root','--','python3','-'],input='RESUME='+repr('--resume-test' in sys.argv)+'\n'+payload,text=True,timeout=90).returncode)

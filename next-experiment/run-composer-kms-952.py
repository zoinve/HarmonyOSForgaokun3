"""One bounded diskless KVM run; capture only upon the real KMS-visible marker."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent
out = base / 'official-composer-kms-952'
assert not (out / 'result.json').exists() and not (out / 'host.stdout').exists()
manifest = json.loads((out / 'manifest.json').read_text())
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/composer-kms-runtime-952'
runner = r'''
from pathlib import Path
import subprocess,json,hashlib,os,socket,threading,time
o=Path(REMOTE);initrd=o/'initramfs.cpio.gz'
assert hashlib.sha256(initrd.read_bytes()).hexdigest()==DIGEST
kernel=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-882/Image')
assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='fb9dffc643f64c754c4a7a34e6fd3b9de6d60bd1ed2ba2aa6096f25bf7ad5474'
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:exe=(p/'exe').resolve(strict=True).name
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 assert not exe.startswith('qemu-system-'),str(p)
assert not (o/'result.json').exists()
cmd=['qemu-system-aarch64','-machine','virt,gic-version=3','-cpu','host','-accel','kvm','-smp','2','-m','512',
 '-kernel',str(kernel),'-initrd',str(initrd),'-append','console=ttyAMA0 rdinit=/init panic=-1 loglevel=7',
 '-display','egl-headless,rendernode=/dev/dri/renderD128','-device','virtio-gpu-gl-pci','-nic','none',
 '-serial','stdio','-monitor','none','-qmp','unix:'+str(o/'qmp.sock')+',server=on,wait=off','-no-reboot']
gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'
result=dict(command=cmd,disks_attached=0,desktop_verified=False,screenshots=[])
def capture():
 try:
  with socket.socket(socket.AF_UNIX) as s:
   s.settimeout(10);s.connect(str(o/'qmp.sock'));f=s.makefile('rwb',buffering=0);json.loads(f.readline())
   def request(data):
    f.write(json.dumps(data).encode()+b'\n')
    while True:
     msg=json.loads(f.readline())
     if 'error' in msg:raise RuntimeError(msg)
     if 'return' in msg:return msg
   request(dict(execute='qmp_capabilities'))
   request(dict(execute='screendump',arguments=dict(filename=str(o/'kms-test-pattern.ppm'))))
   result['screenshots'].append('kms-test-pattern.ppm')
 except Exception as e:result['screenshot_error']=str(e)
with (o/'serial.log').open('xb') as serial,(o/'stderr.log').open('xb') as err:
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=err,env=dict(os.environ,QEMU_MODULE_DIR=gpu+'/modules',LD_LIBRARY_PATH=gpu+'/root/usr/lib/aarch64-linux-gnu'))
 def consume():
  for line in p.stdout:
   serial.write(line);serial.flush()
   if b'COMPOSER_KMS_VISIBLE' in line:capture()
 reader=threading.Thread(target=consume);reader.start();start=time.monotonic()
 try:result['returncode']=p.wait(timeout=100);result['timed_out']=False
 except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=15);result.update(returncode=p.returncode,timed_out=True)
 reader.join(timeout=15);assert not reader.is_alive()
 result['elapsed_seconds']=time.monotonic()-start
text=(o/'serial.log').read_text(errors='replace')
result['probe_pass']='COMPOSER_FULL_PROBE_PASS' in text
result['four_real_frames']=all('COMPOSER_FRAME_PASS frame='+str(i) in text for i in range(4))
result['child_exit_zero']=any('completed=1 status=0' in line and 'USERSPACE_EXIT' in line for line in text.splitlines())
(o/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''.replace('REMOTE', repr(remote)).replace('DIGEST', repr(manifest['initrd_sha256']))
compile(runner, 'runner-952', 'exec')
(out / 'runner.py').write_text(runner)
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
for name in ('initramfs.cpio.gz', 'runner.py'):
    subprocess.run(['scp', str(out / name), 'matebook:' + remote + '/' + name], check=True)
with (out / 'host.stdout').open('xb') as stdout, (out / 'host.stderr').open('xb') as stderr:
    process = subprocess.run(['ssh', 'matebook', 'sudo -n python3 ' + remote + '/runner.py'], stdout=stdout, stderr=stderr, timeout=180)
for name in ('serial.log', 'stderr.log', 'result.json'):
    subprocess.run(['scp', 'matebook:' + remote + '/' + name, str(out / name)], check=True)
result = json.loads((out / 'result.json').read_text())
for name in result['screenshots']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + name, str(out / name)], check=True)
print(json.dumps(result, indent=2))
assert process.returncode == 0

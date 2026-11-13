"""Build a console-enabled test-only kernel and run real ioctls in diskless QEMU."""
import subprocess

payload = r'''
from pathlib import Path
import gzip,hashlib,json,os,shutil,stat,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');candidate=root/'baremetal-identity-candidate-002'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-qemu-002')
work=root/'baremetal-identity-qemu-002';assert not work.exists() and not local.exists()
full=json.loads((candidate/'full-build.json').read_text());assert full['full_build_success']
prior=json.loads((candidate/'result.json').read_text());src=candidate/'linux'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for n,d in prior['patched_critical_hashes'].items():assert sha(src/n)==d,n
assert shutil.disk_usage(root).free>3*1024**3
work.mkdir();local.mkdir();build=work/'out';build.mkdir()
shutil.copyfile(candidate/'out/.config',build/'.config');native_config=sha(candidate/'out/.config')
probe=root/'baremetal-identity-ioctl-probe-002/init'
assert sha(probe)=='1c22fecac42c3519345e8803e77aac7d14bff06b10499fef0bdd244866ba5f0b'
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-')
report=dict(runtime_verified=False,native_board_tested=False,transactions_tested=False,installed=False,
 reboot_requested=False,storage_devices_attached=False,network_devices_attached=False,hardware_gpu_attached=False)
start=time.monotonic()
def run(args,name,timeout):
 with (work/name).open('xb') as log:r=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name);assert r.returncode==0,name+' failed'
try:
 run([str(src/'scripts/config'),'--file',str(build/'.config'),'--enable','SERIAL_AMBA_PL011','--enable','SERIAL_AMBA_PL011_CONSOLE'],'select.log',30)
 common=['make','-C',str(src),'O='+str(build)]
 run(common+['olddefconfig'],'configure.log',180)
 run([str(src/'scripts/diffconfig'),str(candidate/'out/.config'),str(build/'.config')],'config-diff.txt',30)
 shutil.copyfile(build/'.config',local/'resolved.config')
 run(common+['-j4','Image'],'build.log',7200)
 # Deterministic newc archive: only the static test init, mount points, and console.
 raw=bytearray();ino=1
 def entry(name,mode,data=b'',rmajor=0,rminor=0):
  global ino
  fields=[ino,mode,0,0,1,0,len(data),0,0,rmajor,rminor,len(name.encode())+1,0];ino+=1
  raw.extend(b'070701'+b''.join(('%08x'%v).encode() for v in fields));raw.extend(name.encode()+b'\0')
  raw.extend(b'\0'*((-len(raw))%4));raw.extend(data);raw.extend(b'\0'*((-len(raw))%4))
 for name in ['dev','proc','sys']:entry(name,stat.S_IFDIR|0o755)
 entry('dev/console',stat.S_IFCHR|0o600,rmajor=5,rminor=1)
 entry('init',stat.S_IFREG|0o755,probe.read_bytes());entry('TRAILER!!!',0)
 archive=work/'test-init.cpio.gz';archive.write_bytes(gzip.compress(bytes(raw),mtime=0))
 command=['qemu-system-aarch64','-machine','virt,gic-version=3','-cpu','max','-accel','tcg,thread=multi',
  '-m','1024','-smp','2','-nodefaults','-display','none','-monitor','none','-serial','stdio','-nic','none','-no-reboot',
  '-kernel',str(build/'arch/arm64/boot/Image'),'-initrd',str(archive),
  '-append','console=ttyAMA0 rdinit=/init harmony.identity_test=1 panic=-1']
 report['qemu_command']=command
 run(command,'serial.log',180)
 log=(work/'serial.log').read_text(errors='replace')
 assert 'IDENTITY002_PASS checks=' in log and 'IDENTITY002_FAIL' not in log,'Real ioctl probe did not pass'
 assert 'Kernel panic' not in log,'Unexpected kernel panic'
 report['probe_result']=[l for l in log.splitlines() if 'IDENTITY002_' in l]
 report['runtime_verified']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start
 report['native_candidate_config_unchanged']=sha(candidate/'out/.config')==native_config
 report['source_critical_unchanged']=all(sha(src/n)==d for n,d in prior['patched_critical_hashes'].items())
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
'''

if __name__ == '__main__':
    r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=7650)
    raise SystemExit(r.returncode)

"""Load original production policy in diskless/networkless QEMU, never on the host."""
import subprocess

payload=r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');candidate=root/'baremetal-identity-candidate-002';src=candidate/'linux'
work=root/'baremetal-selinux-qemu-013';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-selinux-qemu-013')
assert not work.exists() and not local.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
previous=root/'baremetal-identity-qemu-002';assert json.loads((previous/'result.json').read_text())['runtime_verified']
build=previous/'out';kernel=build/'arch/arm64/boot/Image';expected='130f30abc9c9fc8faf1fb84bec268a1cde10fabdc3c93839250f347924f27bad'
assert sha(kernel)==expected;test_config=sha(build/'.config');native_config=sha(candidate/'out/.config')
critical=json.loads((candidate/'result.json').read_text())['patched_critical_hashes']
for n,d in critical.items():assert sha(src/n)==d,n
prep=json.loads((root/'baremetal-selinux-load-013/result.json').read_text())
for name,row in prep['files'].items():
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],name
work.mkdir();local.mkdir();raw=bytearray();ino=1
def entry(name,mode,data=b'',rmajor=0,rminor=0):
 global ino
 fields=[ino,mode,0,0,1,0,len(data),0,0,rmajor,rminor,len(name.encode())+1,0];ino+=1
 raw.extend(b'070701'+b''.join(('%08x'%v).encode()for v in fields));raw.extend(name.encode()+b'\0');raw.extend(b'\0'*((-len(raw))%4));raw.extend(data);raw.extend(b'\0'*((-len(raw))%4))
for name in ['dev','proc','sys']:entry(name,stat.S_IFDIR|0o755)
entry('dev/console',stat.S_IFCHR|0o600,rmajor=5,rminor=1)
for name,row in prep['files'].items():entry(name,stat.S_IFREG|(0o755 if name=='init' else 0o400),Path(row['path']).read_bytes())
entry('TRAILER!!!',0);archive=work/'test-init.cpio.gz';archive.write_bytes(gzip.compress(bytes(raw),mtime=0))
command=['qemu-system-aarch64','-machine','virt,gic-version=3','-cpu','max','-accel','tcg,thread=multi','-m','1024','-smp','2','-nodefaults','-display','none','-monitor','none','-serial','stdio','-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(archive),'-append','console=ttyAMA0 rdinit=/init harmony.selinux_test=1 panic=-1']
report=dict(runtime_verified=False,services_tested=False,installed=False,reboot_requested=False,native_board_tested=False,storage_devices_attached=False,network_devices_attached=False,qemu_command=command,test_kernel_sha256=expected,policy_sha256=prep['files']['policy.31']['sha256'])
start=time.monotonic()
try:
 with (work/'serial.log').open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 log=(work/'serial.log').read_text(errors='replace');assert r.returncode==0,r.returncode
 assert 'SELINUX013_PASS original_policy_loaded=1 enforcing=1 invalid_policy_rejected=1' in log and 'SELINUX013_FAIL' not in log,'Original policy/enforcing probe failed'
 assert 'Kernel panic' not in log
 report['runtime_verified']=True;report['probe_result']=[l for l in log.splitlines()if 'SELINUX013_' in l]
finally:
 if (work/'serial.log').exists():(local/'serial.log').write_bytes((work/'serial.log').read_bytes())
 report.update(elapsed_seconds=time.monotonic()-start,native_candidate_config_unchanged=sha(candidate/'out/.config')==native_config,test_kernel_and_config_unchanged=sha(kernel)==expected and sha(build/'.config')==test_config,source_critical_unchanged=all(sha(src/n)==d for n,d in critical.items()))
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
'''
compile(payload,'selinux-013-qemu','exec')
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
 raise SystemExit(r.returncode)

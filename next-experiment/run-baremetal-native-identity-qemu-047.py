"""Fresh bounded, diskless legacy Binder/enforcing read and missing-opt-in checks."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
payload='sources='+repr({name:(base/name).read_text() for name in [
    'baremetal-native-identity-qemu-047.c','baremetal-native-identity-read-002.c']})+'\n'+r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');profile=root/'baremetal-identity-profile-003'
work=root/'baremetal-native-identity-qemu-047';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-native-identity-qemu-047')
assert not work.exists() and not local.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
kernel=profile/'test-out/arch/arm64/boot/Image';expected='b5f16aa3c807734c69780ff7014fc56151906067f24960cb896755b5e996dcf5'
assert sha(kernel)==expected
configs={str(profile/'out/.config'):sha(profile/'out/.config'),str(profile/'test-out/.config'):sha(profile/'test-out/.config')}
critical=json.loads((root/'baremetal-identity-candidate-002/result.json').read_text())['patched_critical_hashes']
assert all(sha(profile/'linux'/name)==digest for name,digest in critical.items())
work.mkdir();local.mkdir();report=dict(runtime_verified=False,board_tested=False,installed=False,reboot_requested=False,policy_loaded=False,storage_attached=False,network_attached=False,cases=[],files={})
start=time.monotonic()
try:
 for name,output in [('baremetal-native-identity-qemu-047.c','init'),('baremetal-native-identity-read-002.c','probe')]:
  source=work/name;source.write_text(sources[name]);binary=work/output
  r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,text=True,timeout=60)
  (local/(output+'.compile.stdout')).write_text(r.stdout);(local/(output+'.compile.stderr')).write_text(r.stderr);assert r.returncode==0,r.stderr
  assert 'AArch64' in subprocess.check_output(['readelf','-h',str(binary)],text=True)
  report['files'][output]=dict(path=str(binary),bytes=binary.stat().st_size,sha256=sha(binary),source_sha256=sha(source))
 raw=bytearray();ino=1
 def entry(name,mode,data=b'',rmajor=0,rminor=0):
  global ino
  fields=[ino,mode,0,0,1,0,len(data),0,0,rmajor,rminor,len(name.encode())+1,0];ino+=1
  raw.extend(b'070701'+b''.join(('%08x'%v).encode()for v in fields));raw.extend(name.encode()+b'\0');raw.extend(b'\0'*((-len(raw))%4));raw.extend(data);raw.extend(b'\0'*((-len(raw))%4))
 for name in ['dev','proc','sys','run']:entry(name,stat.S_IFDIR|0o755)
 entry('dev/console',stat.S_IFCHR|0o600,rmajor=5,rminor=1)
 for name in ['init','probe']:entry(name,stat.S_IFREG|0o755,(work/name).read_bytes())
 entry('TRAILER!!!',0);archive=work/'test-init.cpio.gz';archive.write_bytes(gzip.compress(bytes(raw),mtime=0))
 for refusal in [False,True]:
  label='refusal' if refusal else 'positive'
  cmdline='console=ttyAMA0 rdinit=/init harmony.identity_read_test=1 enforcing=1 '+('harmony.expect_refusal=1' if refusal else 'harmony.diag=1')+' panic=-1'
  command=['qemu-system-aarch64','-machine','virt,gic-version=3','-cpu','max','-accel','tcg,thread=multi','-m','1024','-smp','2','-nodefaults','-display','none','-monitor','none','-serial','stdio','-nic','none','-no-reboot','-kernel',str(kernel),'-initrd',str(archive),'-append',cmdline]
  path=work/(label+'.serial.log')
  with path.open('xb') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=30)
  log=path.read_text(errors='replace');(local/path.name).write_bytes(path.read_bytes())
  case=dict(name=label,qemu_returncode=r.returncode,command=command,serial_sha256=sha(path),verified=False);report['cases'].append(case)
  assert r.returncode==0 and 'NATIVE_READ047_PASS' in log and 'NATIVE_READ047_FAIL' not in log and 'Kernel panic' not in log,label
  if refusal:
   assert 'requires diagnostic kernel and opt-in' in log and 'child_status=77 mountpoint_removed=1' in log and 'NATIVE_IDENTITY_READ002_PASS' not in log
  else:
   assert 'NATIVE_IDENTITY_READ002_PASS protocol=8 features=5 legacy_binder=1 selinux_active=1 enforcing=1' in log
   assert 'policy_loaded_by_probe=0 transactions_not_tested=1' in log and 'child_status=0 mountpoint_removed=1' in log
  case['verified']=True
 report['runtime_verified']=True
finally:
 for path in work.glob('*.serial.log'):
  if not (local/path.name).exists():(local/path.name).write_bytes(path.read_bytes())
 report.update(elapsed_seconds=time.monotonic()-start,test_kernel_sha256=sha(kernel),kernel_unchanged=sha(kernel)==expected,configs_unchanged=all(sha(Path(p))==d for p,d in configs.items()),critical_source_unchanged=all(sha(profile/'linux'/name)==digest for name,digest in critical.items()))
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
'''
compile(payload,'native-read047-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=220)
    raise SystemExit(r.returncode)

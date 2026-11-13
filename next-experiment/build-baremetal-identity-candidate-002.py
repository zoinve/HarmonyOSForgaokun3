"""Compile identity objects in a fresh source copy; never install or boot a kernel."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent.parent
REFERENCE = Path(r'C:\Users\39255\AppData\Local\Temp\opencode\HarmonyMac-reference-816\ports')
driver = {p.name: p.read_text() for p in (REFERENCE / 'kernel/accesstokenid').iterdir()
          if p.name in ('access_tokenid.c', 'access_tokenid.h', 'Kconfig', 'Makefile')}
assert len(driver) == 4
driver['access_tokenid.c'] = runpy.run_path(str(BASE / 'next-experiment/baremetal-token-driver-002.py'))['build_driver'](driver['access_tokenid.c'])
generator = (REFERENCE / 'tools/make-access-token-patch.py').read_text()
payload = 'driver = ' + repr(driver) + '\ngenerator = ' + repr(generator) + '\n' + r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');original=root/'baremetal-native-build-001'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-candidate-002')
work=root/'baremetal-identity-candidate-002';assert not work.exists();assert not local.exists()
assert shutil.disk_usage(root).free>8*1024**3
manifest=json.loads(Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-kernel-source-staged-001.json').read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
critical=manifest['critical']
for n,d in critical.items():assert sha(original/'linux'/n)==d,n
original_config=sha(original/'out/.config')
work.mkdir();local.mkdir();src=work/'linux';build=work/'out';build.mkdir()
report=dict(work=str(work),compiled=False,source_copy_patched=False,original_source_unchanged=False,
 installed=False,reboot_requested=False,boot_entries_modified=False,runtime_abi_verified=False,
 unsupported_spm='EOPNOTSUPP, matching original SDK kernel; no success stub',artifacts=[])
start=time.monotonic()
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-',PYTHONDONTWRITEBYTECODE='1')
def run(args,name,timeout):
 with (work/name).open('xb') as log:
  r=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert r.returncode==0,name+' failed; numbered work retained'
try:
 run(['cp','-a','--reflink=auto',str(original/'linux'),str(src)],'copy.log',300)
 (work/'make-access-token-patch.py').write_text(generator)
 patch=work/'identity.patch'
 run(['python3',str(work/'make-access-token-patch.py'),str(src),str(patch)],'generate.log',30)
 shutil.copyfile(patch,local/'identity.patch')
 run(['patch','--directory='+str(src),'--batch','--fuzz=0','-p1','-i',str(patch)],'patch.log',30)
 target=src/'drivers/accesstokenid';assert not target.exists();target.mkdir()
 for name,text in driver.items():(target/name).write_text(text)
 report['source_copy_patched']=True
 shutil.copyfile(original/'out/.config',build/'.config')
 run([str(src/'scripts/config'),'--file',str(build/'.config'),'--enable','ACCESS_TOKENID'],'config-select.log',30)
 common=['make','-C',str(src),'O='+str(build)]
 run(common+['olddefconfig'],'configure.log',180)
 config=(build/'.config').read_text().splitlines()
 for required in ['CONFIG_ACCESS_TOKENID=y','CONFIG_ARM64_4K_PAGES=y','CONFIG_ANDROID_BINDER_IPC=y',
                  'CONFIG_ANDROID_BINDERFS=y','CONFIG_SECURITY_SELINUX=y','CONFIG_SECCOMP=y','CONFIG_QCOM_WDT=m']:
  assert required in config,required
 shutil.copyfile(build/'.config',local/'resolved.config')
 run([str(src/'scripts/diffconfig'),str(original/'out/.config'),str(build/'.config')],'config-diff.txt',30)
 run(common+['-j4','drivers/android/binder.o','drivers/accesstokenid/access_tokenid.o'],'build.log',900)
 for name in ['drivers/android/binder.o','drivers/accesstokenid/access_tokenid.o']:
  p=build/name;assert p.is_file() and p.stat().st_size
  elf=subprocess.check_output(['aarch64-linux-gnu-readelf','-h',str(p)],text=True)
  assert 'AArch64' in elf
  report['artifacts'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),elf_header=elf))
 report['patched_critical_hashes']={n:sha(src/n) for n in critical}
 report['driver_hashes']={n:sha(target/n) for n in driver}
 report['compiled']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start
 report['original_source_unchanged']=all(sha(original/'linux'/n)==d for n,d in critical.items())
 report['original_config_unchanged']=sha(original/'out/.config')==original_config
 (work/'result.json').write_text(json.dumps(report,indent=2))
 (local/'result.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
'''

if __name__ == '__main__':
    compile(payload, 'identity-002-build', 'exec')
    r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=1400)
    raise SystemExit(r.returncode)

"""Fresh original-SDK device/security profile; retain candidate 002 and every source byte."""
import subprocess

payload=r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');parent=root/'baremetal-identity-candidate-002'
work=root/'baremetal-identity-profile-003';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-profile-003')
assert not work.exists() and not local.exists()
assert shutil.disk_usage(root).free>8*1024**3
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prior=json.loads((parent/'result.json').read_text());critical=prior['patched_critical_hashes'];driver=prior['driver_hashes']
for n,d in critical.items():assert sha(parent/'linux'/n)==d,n
for n,d in driver.items():assert sha(parent/'linux/drivers/accesstokenid'/n)==d,n
original_config=sha(parent/'out/.config');old=(parent/'out/.config').read_text().splitlines()
baseline_lsm='landlock,lockdown,yama,loadpin,safesetid,integrity,bpf'
new_lsm='landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,bpf'
assert 'CONFIG_LSM="'+baseline_lsm+'"' in old and 'CONFIG_ANDROID_BINDERFS=y' in old
work.mkdir();local.mkdir();src=work/'linux';build=work/'out';build.mkdir();test=work/'test-out';test.mkdir()
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-',PYTHONDONTWRITEBYTECODE='1')
report=dict(compiled=False,installed=False,reboot_requested=False,boot_entries_modified=False,runtime_verified=False,
 config_changes_intended=['ANDROID_BINDERFS: y -> n','LSM: append selinux before bpf, retaining all previous LSMs'],
 enforcing_boot_argument_required=True,artifacts=[],module_inventory=[])
start=time.monotonic()
def run(args,name,timeout=300):
 with (work/name).open('xb') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert r.returncode==0,name+' failed; preserve numbered outputs'
def config_map(path):
 result={}
 for l in path.read_text().splitlines():
  if l.startswith('CONFIG_'):
   k,v=l.split('=',1);result[k]=v
  elif l.startswith('# CONFIG_') and l.endswith(' is not set'):result[l[2:-11]]='n'
 return result
try:
 run(['cp','-a','--reflink=auto',str(parent/'linux'),str(src)],'copy.log')
 shutil.copyfile(parent/'out/.config',build/'.config')
 run([str(src/'scripts/config'),'--file',str(build/'.config'),'--disable','ANDROID_BINDERFS','--set-str','LSM',new_lsm],'config-select.log')
 common=['make','-C',str(src),'O='+str(build)]
 run(common+['olddefconfig'],'configure.log')
 before=config_map(parent/'out/.config');after=config_map(build/'.config')
 changes={k:dict(before=before.get(k),after=after.get(k)) for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
 assert changes=={'CONFIG_ANDROID_BINDERFS':dict(before='y',after='n'),'CONFIG_LSM':dict(before='"'+baseline_lsm+'"',after='"'+new_lsm+'"')},changes
 for k,v in {'CONFIG_ACCESS_TOKENID':'y','CONFIG_ARM64_4K_PAGES':'y','CONFIG_ANDROID_BINDER_IPC':'y','CONFIG_ANDROID_BINDER_DEVICES':'"binder,hwbinder,vndbinder"','CONFIG_SECURITY_SELINUX':'y','CONFIG_SECCOMP':'y','CONFIG_QCOM_WDT':'m'}.items():assert after[k]==v,(k,after.get(k))
 report['config_changes']=changes;shutil.copyfile(build/'.config',local/'resolved.config')
 run(common+['-j4','Image','dtbs','modules'],'build.log',7200)
 for name in ['arch/arm64/boot/Image','arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb','System.map','modules.order','modules.builtin']:
  p=build/name;report['artifacts'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 for p in sorted(build.rglob('*.ko')):
  vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(p)],text=True).strip()
  assert vermagic.split()[0]=='7.1.0-rc3-gaokun3-el2'
  report['module_inventory'].append(dict(path=str(p.relative_to(build)),bytes=p.stat().st_size,sha256=sha(p),vermagic=vermagic))
 assert len(report['module_inventory'])==391
 shutil.copyfile(build/'.config',test/'.config')
 run([str(src/'scripts/config'),'--file',str(test/'.config'),'--enable','SERIAL_AMBA_PL011','--enable','SERIAL_AMBA_PL011_CONSOLE'],'test-console-select.log')
 test_common=['make','-C',str(src),'O='+str(test)]
 run(test_common+['olddefconfig'],'test-configure.log')
 test_changes={k:dict(before=after.get(k),after=config_map(test/'.config').get(k)) for k in after.keys()|config_map(test/'.config').keys() if after.get(k)!=config_map(test/'.config').get(k)}
 assert set(test_changes)=={'CONFIG_SERIAL_AMBA_PL011','CONFIG_SERIAL_AMBA_PL011_CONSOLE'},test_changes
 run(test_common+['-j4','Image'],'test-build.log',7200)
 p=test/'arch/arm64/boot/Image';report['test_kernel']=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
 report['test_config_sha256']=sha(test/'.config');report['native_config_sha256']=sha(build/'.config');report['test_only_config_changes']=test_changes
 report['compiled']=True
finally:
 report.update(elapsed_seconds=time.monotonic()-start,parent_config_unchanged=sha(parent/'out/.config')==original_config,
 parent_source_critical_unchanged=all(sha(parent/'linux'/n)==d for n,d in critical.items()),
 source_critical_unchanged=all(sha(src/n)==d for n,d in critical.items()) if src.exists() else False,
 driver_unchanged=all(sha(src/'drivers/accesstokenid'/n)==d for n,d in driver.items()) if src.exists() else False)
 (work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='module_inventory'},indent=2),flush=True)
'''
compile(payload,'identity-profile-003-build','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=15000)
    raise SystemExit(r.returncode)

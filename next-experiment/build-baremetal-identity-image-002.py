"""Finish the isolated candidate's full kernel/module build; no deployment or reboot."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-identity-candidate-002'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-candidate-002')
assert not (local/'full-build.json').exists() and not (work/'full-build.log').exists()
prior=json.loads((work/'result.json').read_text());assert prior['compiled'] and prior['original_source_unchanged']
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
src=work/'linux';build=work/'out';original=root/'baremetal-native-build-001'
for n,d in prior['patched_critical_hashes'].items():assert sha(src/n)==d,n
for n,d in prior['driver_hashes'].items():assert sha(src/'drivers/accesstokenid'/n)==d,n
config=sha(build/'.config');assert (local/'config-diff.txt').read_text().strip()=='+ACCESS_TOKENID y'
assert shutil.disk_usage(root).free>5*1024**3
baseline=json.loads(Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-kernel-source-staged-001.json').read_text())['critical']
report=dict(full_build_success=False,installed=False,reboot_requested=False,artifacts=[],runtime_abi_verified=False)
start=time.monotonic()
try:
 env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-')
 with (work/'full-build.log').open('xb') as log:
  r=subprocess.run(['make','-C',str(src),'O='+str(build),'-j4','Image','qcom/sc8280xp-huawei-gaokun3.dtb','modules'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
 assert r.returncode==0,'Full build failed; retain all artifacts'
 for name in ['arch/arm64/boot/Image','arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb','System.map','modules.order','modules.builtin']:
  p=build/name;assert p.is_file() and p.stat().st_size
  report['artifacts'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 report['module_count']=sum(1 for _ in build.rglob('*.ko'))
 report['kernel_release']=(build/'include/config/kernel.release').read_text().strip()
 report['full_build_success']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start
 report['source_copy_critical_unchanged']=all(sha(src/n)==d for n,d in prior['patched_critical_hashes'].items())
 report['original_source_unchanged']=all(sha(original/'linux'/n)==d for n,d in baseline.items())
 report['candidate_config_unchanged']=sha(build/'.config')==config
 if (work/'full-build.log').exists():shutil.copyfile(work/'full-build.log',local/'full-build.log')
 (work/'full-build.json').write_text(json.dumps(report,indent=2));(local/'full-build.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
'''

if __name__ == '__main__':
    r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=7350)
    raise SystemExit(r.returncode)

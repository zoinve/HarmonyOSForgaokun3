"""Compile an isolated native hardware baseline, without installing or booting it."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent.parent
out = base / 'reports/baremetal-native-build-001'
assert not out.exists(), 'Completed or partial numbered builds must be preserved'
config_path = '/mnt/harmony-lab/work/baseline-001/native-kernel-baseline/config-7.1.0-rc3-gaokun3-el2+'
config = subprocess.run(['ssh', 'matebook', 'cat ' + config_path],
                        capture_output=True, check=True, timeout=30).stdout
assert hashlib.sha256(config).hexdigest() == 'f9bd4c810fdf7f7cb3a63307a26395c16b88ca79c3078b854e9b5f9f3aec6d8f'
out.mkdir()
(out / 'native-original.config').write_bytes(config)

payload = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tarfile,time
base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
local=base/'reports/baremetal-native-build-001'
work=Path('/home/zoinve/harmony-virgl-883/baremetal-native-build-001')
archive=work.parent/'baremetal-source-001/linux-source.tar.gz'
manifest=json.loads((base/'reports/baremetal-kernel-source-staged-001.json').read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not work.exists()
assert shutil.disk_usage(work.parent).free > 15*1024**3
assert sha(archive)==manifest['archive_sha256']
work.mkdir();src=work/'linux';src.mkdir();build=work/'out';build.mkdir()
with tarfile.open(archive,'r:gz') as tar:tar.extractall(src,filter='data')
for name,digest in manifest['critical'].items():assert sha(src/name)==digest
original=local/'native-original.config'
assert sha(original)=='f9bd4c810fdf7f7cb3a63307a26395c16b88ca79c3078b854e9b5f9f3aec6d8f'
shutil.copyfile(original,build/'.config')
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-')
common=['make','-C',str(src),'O='+str(build)]
start=time.monotonic()
report=dict(work=str(work),source_commit=manifest['commit'],harmony_identity_patch_applied=False,
            existing_source_modified=False,boot_entries_modified=False,native_boot_attempted=False,
            build_success=False,artifacts=[])
def run(args,name,timeout):
 with (work/name).open('xb') as log:
  result=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert result.returncode==0, name+' failed; preserve log and build directory'
try:
 run(common+['olddefconfig'],'configure.log',180)
 final=(build/'.config').read_text()
 # Fail rather than silently losing native storage, graphics, Binder or protections.
 for required in ['CONFIG_BLK_DEV_NVME=m','CONFIG_DRM_MSM=m',
                  'CONFIG_DRM_PANEL_HIMAX_HX83121A=m','CONFIG_ANDROID_BINDER_IPC=y',
                  'CONFIG_ANDROID_BINDERFS=y','CONFIG_SECURITY_SELINUX=y','CONFIG_QCOM_WDT=m']:
  assert required in final.splitlines(),required
 shutil.copyfile(build/'.config',local/'resolved.config')
 run([str(src/'scripts/diffconfig'),str(original),str(build/'.config')],
     'config-diff.txt',30)
 run(common+['-j'+str(min(4,os.cpu_count() or 1)),'Image',
             'qcom/sc8280xp-huawei-gaokun3.dtb','modules'],'build.log',7200)
 for name in ['arch/arm64/boot/Image','arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb',
              'System.map','modules.order','modules.builtin']:
  p=build/name;assert p.is_file() and p.stat().st_size
  report['artifacts'].append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
 report['module_count']=sum(1 for _ in build.rglob('*.ko'))
 report['build_success']=True
finally:
 report['elapsed_seconds']=time.monotonic()-start
 report['critical_source_files_unchanged']=all(sha(src/n)==d for n,d in manifest['critical'].items())
 for name in ['configure.log','build.log','config-diff.txt']:
  if (work/name).exists():shutil.copyfile(work/name,local/name)
 (work/'result.json').write_text(json.dumps(report,indent=2))
 (local/'result.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2),flush=True)
'''
compile(payload, 'native-build-payload', 'exec')
subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
               text=True, check=True, timeout=7500)

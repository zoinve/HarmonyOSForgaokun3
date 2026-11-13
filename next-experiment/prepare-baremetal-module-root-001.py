"""Prepare and inspect an isolated module tree; never install/load host modules."""
from pathlib import Path
import json
import subprocess

report = Path(__file__).resolve().parent.parent / 'reports/baremetal-module-root-001.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
work=Path('/mnt/harmony-lab/work')
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(work)],text=True).strip()=='/dev/nvme0n1p4'
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(work)],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
source=work/'native-build-001/artifacts'
m=json.loads((source.parent/'native-artifacts-manifest.json').read_text())
release=m['kernel_release'];assert release=='7.1.0-rc3-gaokun3-el2'
dest=work/'native-module-root-001';assert not dest.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[row for row in m['files'] if row['name'].endswith('.ko') or row['name'] in ['modules.order','modules.builtin','modules.builtin.modinfo']]
assert sum(row['name'].endswith('.ko') for row in rows)==391
for row in rows:
 p=source/row['name'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
system_map=next(row for row in m['files'] if row['name']=='System.map')
assert sha(source/'System.map')==system_map['sha256']
dest.mkdir();module_root=dest/'lib/modules'/release
for row in rows:
 name=row['name'];target=module_root/('kernel/'+name if name.endswith('.ko') else name)
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(source/name,target)
 assert sha(target)==row['sha256']
config=dest/'etc/modprobe.d';config.mkdir(parents=True)
env=dict(os.environ);env.pop('MODPROBE_OPTIONS',None)
depmod=shutil.which('depmod') or '/usr/sbin/depmod'
r=subprocess.run([depmod,'-b',str(dest),'-e','-F',str(source/'System.map'),release],capture_output=True,text=True,env=env)
(dest/'depmod.stdout').write_text(r.stdout);(dest/'depmod.stderr').write_text(r.stderr)
assert r.returncode==0,(r.returncode,r.stderr)
assert not r.stderr.strip(),r.stderr
modprobe=shutil.which('modprobe') or '/usr/sbin/modprobe'
checks=[]
for name in ['nvme','msm','panel_himax_hx83121a','i2c_hid_of','huawei_gaokun_ec','qcom_wdt']:
 command=[modprobe,'--dirname',str(dest),'--set-version',release,'--config',str(config),'--show-depends',name]
 r=subprocess.run(command,capture_output=True,text=True,env=env)
 checks.append(dict(module=name,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 assert r.returncode==0 and not r.stderr.strip(),checks[-1]
 for line in r.stdout.splitlines():
  if line.startswith('insmod '):
   p=Path(line.split()[1]);assert p.is_relative_to(module_root) and p.is_file(),line
for row in rows:assert sha(source/row['name'])==row['sha256']
result=dict(destination=str(dest),kernel_release=release,module_count=391,
 dependency_checks=checks,depmod_no_warnings=True,source_modules_unchanged=True,
 installed_to_host=False,modules_loaded=False,boot_entries_modified=False,native_boot_attempted=False)
(dest/'preparation-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
compile(payload, 'prepare-isolated-module-root', 'exec')
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=payload,
                   text=True, capture_output=True, check=True, timeout=300)
result = json.loads(r.stdout)
assert result['module_count'] == 391 and result['depmod_no_warnings']
report.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({key: result[key] for key in ['destination', 'kernel_release', 'module_count',
                                            'depmod_no_warnings', 'modules_loaded', 'native_boot_attempted']}, indent=2))

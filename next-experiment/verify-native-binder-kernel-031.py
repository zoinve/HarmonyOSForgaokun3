"""Read-only compiled kernel and unchanged module-contract checks, not an app test."""
import subprocess
payload=r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
old=root/'baremetal-identity-profile-003';new=root/'native-binder-kernel-031'
r=json.loads((new/'result.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(r['image'])==r['sha256']
assert r['release']==(old/'out/include/config/kernel.release').read_text().strip()=='7.1.0-rc3-gaokun3-el2'
assert sha(new/'out/.config')==sha(old/'out/.config')==r['config_sha256']
assert '# CONFIG_MODVERSIONS is not set' in (new/'out/.config').read_text()
for n,h in r['source_before'].items():assert sha(old/'linux'/n)==h
for n,h in r['source_after'].items():assert sha(new/'linux'/n)==h
symbols=subprocess.check_output(['aarch64-linux-gnu-nm','--defined-only',str(new/'out/vmlinux')],text=True)
exports={line.split()[-1][len('__ksymtab_'):] for line in symbols.splitlines() if line.split()[-1].startswith('__ksymtab_')}
required={line.split()[1] for line in (old/'out/Module.symvers').read_text().splitlines() if line.split()[2]=='vmlinux'}
assert required and not required-exports,sorted(required-exports)
print(json.dumps(dict(image_sha256=r['sha256'],matching_release_config=True,old_kernel_exports_retained=len(required),old_source_unchanged=True,module_external_abi_not_modified=True,native_binder_runtime_tested=False,application_fix_verified=False)))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

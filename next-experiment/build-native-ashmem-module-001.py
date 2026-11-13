"""Build reference ashmem for the retained target kernel; never load in Ubuntu."""
import subprocess
payload=r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883');out=root/'native-ashmem-module-001';out.mkdir()
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/kernel/ashmem')
hashes={n:hashlib.sha256((ref/n).read_bytes()).hexdigest() for n in ['hmos_ashmem.c','ashmem-uapi.h']}
s=(ref/'hmos_ashmem.c').read_text()
assert s.count('mm_page_size(desc->mm)')==1
# Target kernel has fixed 4-KiB granules, not HarmonyMac's mixed-granule extension.
s=s.replace('mm_page_size(desc->mm)','PAGE_SIZE')
(out/'hmos_ashmem.c').write_text(s);(out/'ashmem-uapi.h').write_bytes((ref/'ashmem-uapi.h').read_bytes())
(out/'Makefile').write_text('obj-m += hmos_ashmem.o\n')
k=root/'baremetal-identity-profile-003/out'
assert (k/'include/config/kernel.release').read_text().strip()=='7.1.0-rc3-gaokun3-el2'
assert 'CONFIG_ARM64_4K_PAGES=y' in (k/'.config').read_text()
args=['make','-C',str(k),'ARCH=arm64','CROSS_COMPILE=aarch64-linux-gnu-',f'M={out}','modules']
p=subprocess.run(args,text=True,capture_output=True)
(out/'build.stdout').write_text(p.stdout);(out/'build.stderr').write_text(p.stderr);p.check_returncode()
assert all(hashlib.sha256((ref/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
d=dict(module_sha256=hashlib.sha256((out/'hmos_ashmem.ko').read_bytes()).hexdigest(),reference_sources=hashes,reference_sources_unchanged=True,loaded_in_ubuntu=False,target_granule=4096,compile_command=args)
(out/'result.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300).returncode)

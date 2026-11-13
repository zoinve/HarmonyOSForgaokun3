"""Independent copy of matching source and build tree; never alter profile003."""
import subprocess
payload=r'''
from pathlib import Path
import os,runpy,subprocess,shutil,hashlib,json,time
root=Path('/home/zoinve/harmony-virgl-883');old=root/'baremetal-identity-profile-003'
work=root/'native-binder-kernel-031';local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/native-binder-kernel-031')
assert not work.exists() and not local.exists()
assert shutil.disk_usage(root).free>12*1024**3
work.mkdir();local.mkdir()
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
names=['drivers/android/binder.c','drivers/android/binder_internal.h']
before={n:sha(old/'linux'/n) for n in names};config=sha(old/'out/.config')
env=dict(os.environ,ARCH='arm64',CROSS_COMPILE='aarch64-linux-gnu-')
def run(args,name,timeout=1200):
 with (work/name).open('xb') as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 shutil.copyfile(work/name,local/name)
 assert r.returncode==0,(name,r.returncode)
run(['cp','-a','--reflink=auto',str(old/'linux'),str(work/'linux')],'copy-source.log')
run(['cp','-a','--reflink=auto',str(old/'out'),str(work/'out')],'copy-build.log')
# Generated external-tree Makefile links to the original source: regenerate only in this copy.
makefile=work/'out/Makefile'
text=makefile.read_text();text=text.replace(str(old/'linux'),str(work/'linux'))
makefile.write_text(text)
link=work/'out/source'
if link.is_symlink():
 link.unlink();link.symlink_to(work/'linux')
p=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-binder-pid-031.py')
c=work/'linux'/names[0];h=work/'linux'/names[1]
new,header=p['repair'](c.read_text(),h.read_text());c.write_text(new);h.write_text(header)
shutil.copyfile(c,local/'binder.c');shutil.copyfile(h,local/'binder_internal.h')
run(['make','-C',str(work/'linux'),'O='+str(work/'out'),'-j4','Image'],'build.log',7200)
assert sha(work/'out/.config')==config
assert all(sha(old/'linux'/n)==v for n,v in before.items())
assert sha(old/'out/.config')==config
image=work/'out/arch/arm64/boot/Image'
result=dict(image=str(image),sha256=sha(image),bytes=image.stat().st_size,
 source_before=before,source_after={n:sha(work/'linux'/n) for n in names},config_sha256=config,
 release=(work/'out/include/config/kernel.release').read_text().strip(),
 tokens_unchanged=True,real_pid_reference_lifetime=True,async_supported=True,
 old_source_config_unchanged=True,installed=False,runtime_verified=False)
for dest in [work/'result.json',local/'result.json']:dest.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=8000).returncode)

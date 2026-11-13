"""Restore the original SDK /etc symlink so its unchanged loader configuration is visible."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-027.py')))
source=parent['source']
anchor='    require(!symlink("/sdk-system/system", "/system") && !symlink("/system/lib", "/lib"), "original SDK executable and interpreter paths");'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    require(!symlink("/system/etc", "/etc"), "original SDK loader configuration path");')
source=source.replace('SELINUX027_','SELINUX028_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-027','baremetal-sdk-samgr-exec-028')
anchor="policy=dump('vendor.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""root_etc=subprocess.check_output(['debugfs','-R','stat /etc','/mnt/d/Download/pc_all_arm/system.img'],text=True,stderr=subprocess.DEVNULL)
assert 'Fast link dest: "/system/etc"' in root_etc
(work/'original-etc-link.txt').write_text(root_etc)
loader_paths=dump('system.img','/system/etc/ld-musl-aarch64.path','original-loader-paths')
assert '/system/lib64/platformsdk' in loader_paths.read_text()
"""+anchor)
compile(payload,'samgr-exec028-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

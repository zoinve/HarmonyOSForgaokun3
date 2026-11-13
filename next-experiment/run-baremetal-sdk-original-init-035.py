"""Same bounded handoff, with explicit virtio serials rather than assumed enumeration."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-034.py')))['payload']
for old,new in [('baremetal-sdk-original-init-qemu-034','baremetal-sdk-original-init-qemu-035'),
                ('baremetal-sdk-original-init-034','baremetal-sdk-original-init-035'),('ORIGINAL_INIT034_','ORIGINAL_INIT035_')]:
    assert old in payload;payload=payload.replace(old,new)
old="'virtio-blk-device,drive='+identity]"
assert payload.count(old)==1
payload=payload.replace(old,"'virtio-blk-device,drive='+identity+',serial='+{'system.img':'sdk-system','vendor.img':'sdk-vendor','sys_prod.img':'sdk-sysprod'}[filename]]")
compile(payload,'original-init-035-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(r.returncode)

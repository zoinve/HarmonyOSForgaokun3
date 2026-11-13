"""Original loader namespace configuration, bounded real samgr domain observation only."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-027.py')))['payload']
for old,new in [('baremetal-selinux-qemu-027','baremetal-selinux-qemu-028'),
                ('baremetal-sdk-samgr-exec-027','baremetal-sdk-samgr-exec-028'),('SELINUX027_','SELINUX028_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec028-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

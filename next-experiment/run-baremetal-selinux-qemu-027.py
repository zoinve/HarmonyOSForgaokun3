"""Original fstab-consistent read-only mount, unchanged enforcing production policy."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-026.py')))['payload']
for old,new in [('baremetal-selinux-qemu-026','baremetal-selinux-qemu-027'),
                ('baremetal-sdk-samgr-exec-026','baremetal-sdk-samgr-exec-027'),('SELINUX026_','SELINUX027_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec027-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

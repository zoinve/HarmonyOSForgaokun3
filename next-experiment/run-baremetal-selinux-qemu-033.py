"""Actual production policy authorizes init tracing its direct samgr child; preserve ping failure."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-032.py')))['payload']
for old,new in [('baremetal-selinux-qemu-032','baremetal-selinux-qemu-033'),
                ('baremetal-sdk-samgr-exec-032','baremetal-sdk-samgr-exec-033'),('SELINUX032_','SELINUX033_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec033-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

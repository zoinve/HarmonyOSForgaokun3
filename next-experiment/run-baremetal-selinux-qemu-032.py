"""Same enforcing original-service probe; collect exact Binder failure diagnostics."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-031.py')))['payload']
for old,new in [('baremetal-selinux-qemu-031','baremetal-selinux-qemu-032'),
                ('baremetal-sdk-samgr-exec-031','baremetal-sdk-samgr-exec-032'),('SELINUX031_','SELINUX032_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec032-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

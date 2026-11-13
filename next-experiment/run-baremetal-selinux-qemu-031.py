"""Capture bounded startup diagnostics without weakening the genuine-manager ping requirement."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-030.py')))['payload']
for old,new in [('baremetal-selinux-qemu-030','baremetal-selinux-qemu-031'),
                ('baremetal-sdk-samgr-exec-030','baremetal-sdk-samgr-exec-031'),('SELINUX030_','SELINUX031_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec031-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

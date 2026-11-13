"""Bounded original samgr execution with a genuine urandom node, original policy unchanged."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-028.py')))['payload']
for old,new in [('baremetal-selinux-qemu-028','baremetal-selinux-qemu-029'),
                ('baremetal-sdk-samgr-exec-028','baremetal-sdk-samgr-exec-029'),('SELINUX028_','SELINUX029_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'samgr-exec029-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

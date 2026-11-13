"""Enforcing unchanged SDK policy, with post-load original-label restoration."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-016.py')))['payload']
for old,new in [('baremetal-selinux-qemu-016','baremetal-selinux-qemu-017'),
                ('baremetal-selinux-load-016','baremetal-selinux-load-017'),('SELINUX016_','SELINUX017_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-017-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

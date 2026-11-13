"""Unchanged enforcing kernel/policy, with separate policy and driver rejection assertions."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-022.py')))['payload']
for old,new in [('baremetal-selinux-qemu-022','baremetal-selinux-qemu-023'),
                ('baremetal-selinux-identity-022','baremetal-selinux-identity-023'),('SELINUX022_','SELINUX023_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-023-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

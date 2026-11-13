"""Unchanged enforcing kernel/policy, with RAM device filesystem and original console label."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-017.py')))['payload']
for old,new in [('baremetal-selinux-qemu-017','baremetal-selinux-qemu-018'),
                ('baremetal-selinux-load-017','baremetal-selinux-load-018'),('SELINUX017_','SELINUX018_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-018-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

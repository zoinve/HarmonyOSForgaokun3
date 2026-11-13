"""Repeat with unchanged profile003 kernel/policy and faithful metadata-denial expectations."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-021.py')))['payload']
for old,new in [('baremetal-selinux-qemu-021','baremetal-selinux-qemu-022'),
                ('baremetal-selinux-identity-020','baremetal-selinux-identity-022'),('SELINUX020_','SELINUX022_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-022-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

"""Same enforcing kernel and policy, now with correctly labelled isolated init fixture."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-015.py')))['payload']
for old,new in [('baremetal-selinux-qemu-015','baremetal-selinux-qemu-016'),
                ('baremetal-selinux-load-013','baremetal-selinux-load-016'),('SELINUX013_','SELINUX016_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-016-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

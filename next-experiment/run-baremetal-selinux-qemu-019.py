"""Original policy, positive init-console and negative rootfs-console paths."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-018.py')))['payload']
for old,new in [('baremetal-selinux-qemu-018','baremetal-selinux-qemu-019'),
                ('baremetal-selinux-load-018','baremetal-selinux-load-019'),('SELINUX018_','SELINUX019_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-019-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

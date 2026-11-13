"""Keep all LSMs and explicitly request enforcing at boot for the DEVELOPMENT configuration."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-014.py')))['payload']
for old,new in [('baremetal-selinux-qemu-014','baremetal-selinux-qemu-015'),
                ('integrity,selinux,bpf panic=-1','integrity,selinux,bpf enforcing=1 panic=-1')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'selinux-015-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

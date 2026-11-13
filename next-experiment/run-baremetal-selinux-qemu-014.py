"""Retest identical production policy/init with SELinux added to the complete baseline LSM list."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-013.py')))['payload']
for old,new in [("work=root/'baremetal-selinux-qemu-013'","work=root/'baremetal-selinux-qemu-014'"),
                ('reports/baremetal-selinux-qemu-013','reports/baremetal-selinux-qemu-014'),
                ('harmony.selinux_test=1 panic=-1','harmony.selinux_test=1 lsm=landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,bpf panic=-1')]:
    assert payload.count(old)==1,old
    payload=payload.replace(old,new)
anchor="report['runtime_verified']=True;"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"report['selinux_explicitly_added_to_baseline_lsm']=True;"+anchor)
compile(payload,'selinux-014-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

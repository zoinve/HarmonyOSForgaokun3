"""Same unchanged SDK/policy/kernel, additionally require an original-manager Binder reply."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-029.py')))['payload']
for old,new in [('baremetal-selinux-qemu-029','baremetal-selinux-qemu-030'),
                ('baremetal-sdk-samgr-exec-029','baremetal-sdk-samgr-exec-030'),('SELINUX029_','SELINUX030_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor=" report['selinux_explicitly_added_to_baseline_lsm']=True;"
assert payload.count(anchor)==1
payload=payload.replace(anchor," assert 'SELINUX030_PING_RESULT received=1 result=0' in log\n"+anchor)
compile(payload,'samgr-exec030-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

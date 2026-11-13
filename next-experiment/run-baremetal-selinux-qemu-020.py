"""Real device ABI plus positive/negative authorization tests, no service-role substitution."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-019.py')))['payload']
for old,new in [('baremetal-selinux-qemu-019','baremetal-selinux-qemu-020'),
                ('baremetal-selinux-load-019','baremetal-selinux-identity-020'),('SELINUX019_','SELINUX020_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor=" report['selinux_explicitly_added_to_baseline_lsm']=True"
assert payload.count(anchor)==1
payload=payload.replace(anchor," assert 'SELINUX020_IDENTITY_PASS actual_devices=1 original_labels=1 task_token_roundtrip=1 nonowner_denied=1 spm_unsupported=1 protocol=8 features=5 init_context_manager_denied=1' in log\n report['actual_identity_devices_under_enforcing_policy_verified']=True\n"+anchor)
compile(payload,'selinux-020-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

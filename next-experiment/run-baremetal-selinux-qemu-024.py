"""Same 023 binary/kernel/policy; correct stale result matcher to its stronger split rejection markers."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-023.py')))['payload']
old="assert 'SELINUX023_IDENTITY_PASS actual_devices=1 original_labels=1 task_token_roundtrip=1 nonowner_denied=1 spm_unsupported=1 protocol=8 features=5 init_context_manager_denied=1' in log"
new="assert 'SELINUX023_IDENTITY_PASS actual_devices=1 original_labels_set=1 metadata_read_denied=1 task_token_roundtrip=1 nonowner_denied=1 spm_version_policy_denied=1 spm_allowed_command_unsupported=1 protocol=8 features=5 init_context_manager_denied=1' in log"
assert payload.count(old)==1
payload=payload.replace(old,new).replace('baremetal-selinux-qemu-023','baremetal-selinux-qemu-024')
compile(payload,'selinux-024-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=160)
    raise SystemExit(r.returncode)

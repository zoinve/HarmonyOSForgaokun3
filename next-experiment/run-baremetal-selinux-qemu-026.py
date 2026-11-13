"""Original executable and original policy, bounded guest-only lifecycle; no token fabrication."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-selinux-qemu-025.py')))['payload']
for old,new in [('baremetal-selinux-qemu-025','baremetal-selinux-qemu-026'),
                ('baremetal-sdk-system-read-025','baremetal-sdk-samgr-exec-026'),('SELINUX025_','SELINUX026_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor=" report['original_sdk_readonly_filesystem_verified']=True"
assert payload.count(anchor)==1
payload=payload.replace(anchor," assert 'SELINUX026_EXEC_PASS original_binary=1 actual_samgr_domain=1 uid=5555 gid=5555 tokens_not_fabricated=1 policy_unchanged=1 services_ready=0 desktop_not_tested=1' in log\n report['original_samgr_exec_domain_verified']=True\n report['services_ready']=False\n"+anchor)
compile(payload,'sdk-samgr-exec-026-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

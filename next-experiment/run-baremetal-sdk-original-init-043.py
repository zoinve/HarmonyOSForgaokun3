"""Observe actual SA reply transport; semantic verification remains a separate strict check."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-040.py')))['payload']
for old,new in [('original-init-qemu-040','original-init-qemu-043'),('original-init-040','original-init-043'),
                ('harmony-sdk-qemu040-','harmony-sdk-qemu043-'),('ORIGINAL_INIT040_','ORIGINAL_INIT043_')]:
    assert old in payload;payload=payload.replace(old,new)
payload=payload.replace("report['genuine_manager_ping_under_enforcing_policy_observed']",
                        "report['genuine_manager_list_reply_under_enforcing_policy_observed']")
payload=payload.replace('MANAGER_PING_PASS','MANAGER_LIST_REPLY_OBSERVED')
anchor="  report['observer_failure_observed']="
assert payload.count(anchor)==1
payload=payload.replace(anchor,"  report['sa_list_semantically_verified']=False # independently decode the captured reply first\n"+anchor)
compile(payload,'original-init-043-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)

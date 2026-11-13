"""Same faithful read-only boot contract; independently report genuine manager ping evidence."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-038.py')))['payload']
for old,new in [('baremetal-sdk-original-init-qemu-038','baremetal-sdk-original-init-qemu-039'),
                ('baremetal-sdk-original-init-038','baremetal-sdk-original-init-039'),
                ('harmony-sdk-qemu038-','harmony-sdk-qemu039-'),('ORIGINAL_INIT038_','ORIGINAL_INIT039_')]:
    assert old in payload;payload=payload.replace(old,new)
anchor="  report['helper_failure_observed']=b'ORIGINAL_INIT039_FAIL' in data"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\n  report['genuine_manager_ping_under_enforcing_policy_observed']=b'ORIGINAL_INIT039_MANAGER_PING_PASS' in data\n  report['observer_failure_observed']=b'ORIGINAL_INIT039_OBSERVER_FAIL' in data")
compile(payload,'original-init-039-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)

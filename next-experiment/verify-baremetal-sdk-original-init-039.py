"""Read-only independent check; distinguish a manager reply from overall service readiness."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-038.py')))['payload']
payload=payload.replace('original-init-qemu-038','original-init-qemu-039').replace('original-init-038','original-init-039').replace('ORIGINAL_INIT038_','ORIGINAL_INIT039_')
anchor=" d=dict(serial_sha256="
# Original verifier is top-level Python, not indented.
anchor=anchor.lstrip()
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""ping=b'ORIGINAL_INIT039_MANAGER_PING_PASS' in s
observer_failed=b'ORIGINAL_INIT039_OBSERVER_FAIL' in s
assert r['genuine_manager_ping_under_enforcing_policy_observed']==ping
assert r['observer_failure_observed']==observer_failed
if ping:
 assert not observer_failed
 assert b'ORIGINAL_INIT039_OBSERVER domain=u:r:init:s0 enforcing=1 replacement_manager=0 tokens_modified=0' in s
 assert b'ORIGINAL_INIT039_PING_REPLY' in s
 assert b'ORIGINAL_INIT039_PING_RESULT received=1 result=0' in s
 assert b'genuine_handle0_reply=1 full_services_ready=0 desktop_not_tested=1' in s
"""+anchor)
anchor=' service_readiness_not_claimed=True,'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'genuine_manager_ping_observed=ping,observer_failure_observed=observer_failed,')
compile(payload,'verify-original-init-039','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

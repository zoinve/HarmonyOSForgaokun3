"""Independently preserve and interpret terminal rejection without declaring service readiness."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-043.py')))['payload']
for old,new in [('original-init-qemu-043','original-init-qemu-044'),('original-init-043','original-init-044'),
                ('ORIGINAL_INIT043_','ORIGINAL_INIT044_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor='d=dict(serial_sha256='
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""identities=re.findall(rb'ORIGINAL_INIT044_CALLER_IDENTITY available=(\\d+) self_token=([0-9a-f]{16}) original_sdk_type_flag=(-?\\d+) read_errno=(\\d+) tokens_modified=0',s)
assert len(replies)==1 and len(identities)==1, 'one actual terminal reply and one own-identity observation required'
available,token,typeflag,read_errno=identities[0]
identity=dict(available=bool(int(available)),self_token_hex=token.decode(),original_sdk_type_flag=int(typeflag),read_errno=int(read_errno),tokens_modified=False)
if identity['available']:
 value=int(token,16);assert int(typeflag)==(-1 if value==0 else (value>>27)&3)
assert b'ORIGINAL_INIT044_MANAGER_LIST_REJECTED terminal=1 enforcing=1 tokens_modified=0 full_services_ready=0' in s
assert r['genuine_list_terminal_rejection_observed'] and not semantic['verified']
"""+anchor)
anchor='sa_list_semantic_verification=semantic,'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'caller_identity_observation=identity,terminal_rejection_verified=True,')
compile(payload,'original-init-044-independent-audit','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

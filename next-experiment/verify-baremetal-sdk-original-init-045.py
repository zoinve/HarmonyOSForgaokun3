"""Independently verify preservation and captured SA-object evidence, not whole-service readiness."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-038.py')))['payload']
payload=payload.replace('original-init-qemu-038','original-init-qemu-045').replace('original-init-038','original-init-045').replace('ORIGINAL_INIT038_','ORIGINAL_INIT045_')
anchor='d=dict(serial_sha256='
assert payload.count(anchor)==1
payload=payload.replace(anchor,r'''import re,struct
replies=re.findall(rb'ORIGINAL_INIT045_CHECK_REPLY uid=(\d+) bytes=(\d+) offsets=(\d+) flags=(\d+) transport_result=(-?\d+) hex=([0-9a-f]*)',s)
objects=re.findall(rb'ORIGINAL_INIT045_REMOTE_OBJECT sa_id=1912 handle=(\d+) uid=(\d+) offsets=(\d+) tokens_modified=0 service_ping_not_tested=1',s)
object_evidence=[]
for uid,size,offsets,flags,status,encoded in replies:
 raw=bytes.fromhex(encoded.decode());assert len(raw)==int(size)
 if int(status)==0:
  assert int(uid)==5555 and not int(flags)&8 and int(offsets)==8
  matches=[(offset,struct.unpack_from('<I',raw,offset+8)[0]) for offset in range(0,len(raw)-23,4) if struct.unpack_from('<I',raw,offset)[0]==0x73682a85]
  assert len(matches)==1 and matches[0][1]>0, 'one genuine remote handle in captured parcel required'
  assert (str(matches[0][1]).encode(),b'5555',b'8') in objects
  object_evidence.append(dict(sa_id=1912,remote_handle=matches[0][1],parcel_object_offset=matches[0][0],sender_uid=5555,reply_sha256=hashlib.sha256(raw).hexdigest()))
observed=bool(object_evidence)
assert r['genuine_remote_sa_object_observed']==observed
if observed:
 assert r['genuine_manager_check_reply_under_enforcing_policy_observed']
 assert b'ORIGINAL_INIT045_OBSERVER domain=u:r:init:s0 enforcing=1 replacement_manager=0 tokens_modified=0' in s
 assert b'ORIGINAL_INIT045_MANAGER_CHECK_REPLY_OBSERVED' in s and not r['observer_failure_observed']
identities=re.findall(rb'ORIGINAL_INIT045_CALLER_IDENTITY available=(\d+) self_token=([0-9a-f]{16}) original_sdk_type_flag=(-?\d+) read_errno=(\d+) tokens_modified=0',s)
for available,token,typeflag,error in identities:
 if int(available):
  value=int(token,16);assert int(typeflag)==(-1 if value==0 else (value>>27)&3)
'''+anchor)
anchor=' service_readiness_not_claimed=True,'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'genuine_remote_sa_object_verified=observed,remote_object_evidence=object_evidence,actual_replies_observed=len(replies),')
compile(payload,'verify-original-init-045','exec')
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
 raise SystemExit(r.returncode)

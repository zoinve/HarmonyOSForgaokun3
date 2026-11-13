"""Preservation audit plus strict, separately reported semantic interpretation of real reply."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-040.py')))['payload']
payload=payload.replace('original-init-qemu-040','original-init-qemu-043').replace('original-init-040','original-init-043').replace('ORIGINAL_INIT040_','ORIGINAL_INIT043_')
payload=payload.replace('MANAGER_PING_PASS','MANAGER_LIST_REPLY_OBSERVED').replace('genuine_manager_ping','genuine_manager_list_reply')
anchor='d=dict(serial_sha256='
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""import re,struct,runpy
replies=re.findall(rb'ORIGINAL_INIT043_LIST_REPLY uid=(\\d+) bytes=(\\d+) offsets=(\\d+) flags=(\\d+) transport_result=(-?\\d+) hex=([0-9a-f]*)',s)
semantic=dict(verified=False,error='no complete list reply captured',abilities=[],replies_observed=len(replies),unique_replies=[])
for captured in replies:
 uid,size,offsets,flags,transport,encoded=captured
 raw=bytes.fromhex(encoded.decode());assert len(raw)==int(size)
 detail=dict(sender_uid=int(uid),reply_bytes=len(raw),offsets_bytes=int(offsets),flags=int(flags),transport_result=int(transport),reply_sha256=hashlib.sha256(raw).hexdigest(),reply_hex=encoded.decode())
 if detail not in semantic['unique_replies']:semantic['unique_replies'].append(detail)
 try:
  if int(uid)!=5555 or int(offsets)!=0 or int(flags)&8 or int(transport)!=0:
   raise ValueError(f'unexpected sender, objects, or Binder transport status: uid={int(uid)} offsets={int(offsets)} flags={int(flags)} result={int(transport)}')
  decode=runpy.run_path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/baremetal-samgr-list-reply-043.py')['decode_list_reply']
  semantic['abilities']=decode(raw)
  semantic['verified']=True;semantic['error']=None
 except ValueError as error:
  if not semantic['verified']:semantic['error']=str(error)
assert r['sa_list_semantically_verified'] is False # runner never predeclares semantic success
"""+anchor)
anchor=' service_readiness_not_claimed=True,'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'sa_list_semantic_verification=semantic,')
compile(payload,'verify-original-init-043','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

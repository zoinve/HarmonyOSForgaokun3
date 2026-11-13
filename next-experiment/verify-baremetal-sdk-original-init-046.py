"""Preservation and authentic reply-metadata evidence; never promote to full readiness."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-040.py')))['payload']
payload=payload.replace('original-init-qemu-040','original-init-qemu-046').replace('original-init-040','original-init-046').replace('ORIGINAL_INIT040_','ORIGINAL_INIT046_')
anchor="out.write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))"
assert payload.count(anchor)==1
payload=payload.replace(anchor,r'''
import re
rows=re.findall(rb'ORIGINAL_INIT046_REPLY_SENDER result=(-?\d+) errno=(\d+) token=([0-9a-f]{16}) first=([0-9a-f]{16}) pid=(\d+) reserved0=(\d+) reserved1=(\d+) uid=(\d+) tokens_modified=0',s)
assert len(rows)==1,rows
row=rows[0]
observed=dict(result=int(row[0]),errno=int(row[1]),token_id_hex=row[2].decode(),
 first_token_id_hex=row[3].decode(),pid=int(row[4]),reserved0=int(row[5]),reserved1=int(row[6]),uid=int(row[7]))
observed['sdk_token_type_flag']=((int(observed['token_id_hex'],16)>>27)&3) if int(observed['token_id_hex'],16) else -1
if ping:
 assert observed['result']==0 and observed['pid']>1 and observed['uid']==5555
 assert int(observed['token_id_hex'],16) and observed['reserved0']==observed['reserved1']==0
d['reply_sender_metadata']=observed
d['authentic_nonzero_sender_metadata_observed']=bool(ping and observed['result']==0)
d['sender_native_token_type_observed']=bool(ping and observed['sdk_token_type_flag']==1)
d['identities_modified']=False
'''+anchor)
compile(payload,'verify-original-init-046','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

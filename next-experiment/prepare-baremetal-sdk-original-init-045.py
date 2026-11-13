"""Query a genuine SA using the original CheckSystemAbility wire contract; never change identity."""
from pathlib import Path
import hashlib
import runpy
import struct
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-044.py')))
source=parent['source']
original=bytes.fromhex(parent['parent']['request_evidence']['request_hex'])
assert len(original)==64 and original[-4:]==struct.pack('<i',15)
request=original[:-4]+struct.pack('<i',1912)
old='    static const unsigned char original_request[] = {'+','.join('0x%02x'%b for b in original)+'};'
new='    static const unsigned char original_request[] = {'+','.join('0x%02x'%b for b in request)+'};'
assert source.count(old)==1;source=source.replace(old,new)
anchor='.target.handle=0,.code=5,.flags=0,'
assert source.count(anchor)==1;source=source.replace(anchor,'.target.handle=0,.code=2,.flags=0x200000,')
anchor='static int samgr_ping_030(void)'
assert source.count(anchor)==1
source=source.replace(anchor,Path(__file__).with_name('baremetal-samgr-object-045.h').read_text()+'\n'+anchor)
anchor='                actual_reply = 1;'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
                if (!(tx.flags & TF_STATUS_CODE)) {
                    uint32_t remote_handle=0;
                    require(samgr_object_045(mapping,mapping_size,&tx,&remote_handle)==1,
                            "genuine SA response contains one bounded remote handle");
                    require(tx.sender_euid==5555, "genuine SAMGR query responder UID");
                    dprintf(1,"ORIGINAL_INIT045_REMOTE_OBJECT sa_id=1912 handle=%u uid=%u offsets=%llu tokens_modified=0 service_ping_not_tested=1\\n",
                            remote_handle,tx.sender_euid,(unsigned long long)tx.offsets_size);
                }
''')
anchor='    return samgr_reply_action_044(received, actual_reply, result);'
assert source.count(anchor)==1
# The original Check handler returns 7 when no object is available. Only that case may retry.
source=source.replace(anchor,'    if (actual_reply && result==7) return 0;\n'+anchor)
source=source.replace('ORIGINAL_INIT044_','ORIGINAL_INIT045_').replace('MANAGER_LIST_','MANAGER_CHECK_').replace('_LIST_REPLY ','_CHECK_REPLY ')
evidence=dict(parent['parent']['request_evidence'],request_hex=request.hex(),
              request_sha256=hashlib.sha256(request).hexdigest(),sa_id=1912,transaction_code=2,
              message_option_flags=0x200000,contract_audit='baremetal-sdk-check-ability044-audit.json')
payload='source='+repr(source)+'\nrequest_evidence='+repr(evidence)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-044','baremetal-sdk-original-init-045')
compile(payload,'original-init-045-prepare','exec')
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
 raise SystemExit(r.returncode)

"""Query the genuine SAMGR with bytes produced by the unchanged original SDK encoder."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
encoding=base/'reports/baremetal-sdk-parcel-qemu-042'
assert json.loads((encoding/'result.json').read_text())['original_parcel_encoding_observed']
serial=(encoding/'serial.log').read_bytes()
matches=re.findall(rb'PARCEL042_REQUEST descriptor=ohos.samgr.accessToken code=5 argument=15 bytes=64 hex=([0-9a-f]+)',serial)
assert len(matches)==1 and b'PARCEL042_PASS' in serial
request=bytes.fromhex(matches[0].decode());assert len(request)==64
request_evidence=dict(path=str(encoding/'serial.log'),serial_sha256=hashlib.sha256(serial).hexdigest(),
    request_hex=request.hex(),request_sha256=hashlib.sha256(request).hexdigest(),
    original_proxy_sha256='9b916b2ac342e98da58aded0c71e8da9c98179d0e0ff3933d5a3506c4278d320')
parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-040.py')))
source=parent['source']
anchor='    struct binder_transaction_data tx = {.target.handle = 0, .code = 0x5f504e47, .flags = 0x200000};'
assert source.count(anchor)==1
source=source.replace(anchor,'    static const unsigned char original_request[] = {'+
    ','.join('0x%02x'%b for b in request)+'};\n'+
    '    struct binder_transaction_data tx = {.target.handle=0,.code=5,.flags=0,\n'+
    '        .data_size=sizeof(original_request),.data.ptr.buffer=(uintptr_t)original_request};')
anchor='tx.data_size <= 4096'
assert source.count(anchor)==1
source=source.replace(anchor,'tx.data_size <= 65536')
anchor='                uint32_t free_op = BC_FREE_BUFFER;'
assert source.count(anchor)==1
source=source.replace(anchor,'''                char reply_hex[131073];
                static const char digits[]="0123456789abcdef";
                const unsigned char *reply_data=(const unsigned char *)buffer;
                for(size_t i=0;i<tx.data_size;++i) {
                    reply_hex[2*i]=digits[reply_data[i]>>4];
                    reply_hex[2*i+1]=digits[reply_data[i]&15];
                }
                reply_hex[2*tx.data_size]=0;
                dprintf(1,"ORIGINAL_INIT043_LIST_REPLY uid=%u bytes=%llu offsets=%llu flags=%u transport_result=%d hex=%s\\n",
                    tx.sender_euid,(unsigned long long)tx.data_size,(unsigned long long)tx.offsets_size,
                    tx.flags,result,reply_hex);
'''+anchor)
source=source.replace('ORIGINAL_INIT040_','ORIGINAL_INIT043_')
source=source.replace('MANAGER_PING_PASS','MANAGER_LIST_REPLY_OBSERVED').replace('MANAGER_PING_UNVERIFIED','MANAGER_LIST_UNVERIFIED')
payload='source='+repr(source)+'\nrequest_evidence='+repr(request_evidence)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-040','baremetal-sdk-original-init-043')
anchor='report=dict('
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'request_encoding_evidence=request_evidence,')
compile(payload,'original-init-043-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

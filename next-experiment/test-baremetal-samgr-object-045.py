"""Run the actual bounded Binder remote-object decoder against malformed and valid replies."""
from pathlib import Path
import subprocess

header=Path(__file__).with_name('baremetal-samgr-object-045.h')
assert header.exists(), 'missing real reply object validation'
source=header.read_text()+r'''
#include <assert.h>
int main(void) {
 unsigned char map[256]={0}; struct binder_transaction_data tx={0}; uint32_t handle=0;
 struct flat_binder_object obj={.hdr.type=BINDER_TYPE_HANDLE,.handle=23};
 binder_size_t offset=0;
 memcpy(map+32,&obj,sizeof(obj));memcpy(map+128,&offset,sizeof(offset));
 tx.data.ptr.buffer=(uintptr_t)(map+32);tx.data_size=sizeof(obj);
 tx.data.ptr.offsets=(uintptr_t)(map+128);tx.offsets_size=sizeof(offset);
 assert(samgr_object_045(map,sizeof(map),&tx,&handle)==1 && handle==23);
 tx.flags=TF_STATUS_CODE;assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);tx.flags=0;
 tx.data.ptr.offsets=(uintptr_t)(map+252);assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 tx.data.ptr.offsets=(uintptr_t)(map+128);
 offset=sizeof(obj);memcpy(map+128,&offset,sizeof(offset));assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 offset=0;memcpy(map+128,&offset,sizeof(offset));
 obj.hdr.type=BINDER_TYPE_FD;memcpy(map+32,&obj,sizeof(obj));assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 obj.hdr.type=BINDER_TYPE_HANDLE;obj.handle=0;memcpy(map+32,&obj,sizeof(obj));assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 obj.handle=23;memcpy(map+32,&obj,sizeof(obj));
 tx.data.ptr.buffer=(uintptr_t)(map+250);assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 tx.data.ptr.buffer=(uintptr_t)(map+32);tx.offsets_size=0;assert(samgr_object_045(map,sizeof(map),&tx,&handle)==-1);
 return 0;
}
'''
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='samgr-object045-') as directory:
 p=Path(directory);(p/'test.c').write_text(source)
 subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: remote handle admitted; status, offsets, buffer bounds, FD type, and handle zero rejected')
'''
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=45)
 raise SystemExit(r.returncode)

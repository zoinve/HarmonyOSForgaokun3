"""Real H4 framing and fail-closed vendor operations, without host Bluetooth access."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'native-qca-broker-022.c').exists(),'missing QCA stream broker'
assert (base/'native-qca-vendor-022.c').exists(),'missing QCA vendor adapter'
TEST=r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#define main broker_program_main
#include "native-qca-broker-022.c"
#undef main
#include "ohos_bt_vendor_abi.h"
extern const BtVendorInterfaceT BLUETOOTH_VENDOR_LIB_INTERFACE;
static int callbacks;
static void complete(BtOpResultT result){(void)result;++callbacks;}
int main(void){
 unsigned char reset[]={1,3,12,0}; unsigned char acl[]={2,1,0,3,0,9,8,7};
 unsigned char bad[]={0};
 assert(h4_length(reset,3)==0 && h4_length(reset,4)==4);
 assert(h4_length(acl,5)==8 && h4_length(acl,8)==8);
 assert(h4_length(bad,1)==-1);
 BtVendorCallbacksT cb={.size=sizeof(cb),.initCb=complete};
 int fds[4]={-1,-1,-1,-1};
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.init(&cb,NULL)==0);
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.op(BT_OP_INIT,NULL)==-1 && callbacks==0);
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.op(BT_OP_POWER_ON,NULL)==-1);
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.op(BT_OP_HCI_CHANNEL_OPEN,fds)==-1);
 assert(fds[0]==-1 && callbacks==0);
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.op(BT_OP_LPM_ENABLE,NULL)==-1 && errno==ENOTSUP);
 BLUETOOTH_VENDOR_LIB_INTERFACE.close();return 0;
}
'''
payload='TEST='+repr(TEST)+r'''
from pathlib import Path
import tempfile,subprocess
source=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
with tempfile.TemporaryDirectory(prefix='qca-bridge-022-',dir='/home/zoinve/harmony-virgl-883') as tmp:
 p=Path(tmp);(p/'test.c').write_text(TEST)
 subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror','-I'+str(source),'-I/mnt/d/lab/HarmonyOSForMatebookego/references/L410-HarmonyOS-Adaptations/bluetooth',str(p/'test.c'),str(source/'native-qca-vendor-022.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS H4 boundaries; missing real broker cannot supply FD or success callback; unsupported LPM is not faked')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60).returncode)

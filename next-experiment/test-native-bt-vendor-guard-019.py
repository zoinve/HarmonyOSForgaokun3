"""Missing real transport must fail initialization, never report success."""
from pathlib import Path
import subprocess
source=Path(__file__).with_name('native-bt-vendor-guard-019.c')
assert source.exists(),'missing fail-closed vendor adapter'
test=r'''
#include <assert.h>
#include <errno.h>
#include "ohos_bt_vendor_abi.h"
extern const BtVendorInterfaceT BLUETOOTH_VENDOR_LIB_INTERFACE;
static int called;
static void callback(BtOpResultT result){(void)result;++called;}
int main(void){
 BtVendorCallbacksT cb={.size=sizeof(cb),.initCb=callback};
 unsigned char addr[6]={0};int fds[4]={-1,-1,-1,-1};
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.init(&cb,addr)==-1);
 assert(errno==ENOENT || errno==ENODEV);
 assert(called==0);
 assert(BLUETOOTH_VENDOR_LIB_INTERFACE.op(BT_OP_HCI_CHANNEL_OPEN,fds)==-1);
 assert(called==0 && fds[0]==-1);
 BLUETOOTH_VENDOR_LIB_INTERFACE.close();return 0;
}
'''
script=r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='bt-vendor-guard-019-',dir='/home/zoinve/harmony-virgl-883') as tmp:
 p=Path(tmp);(p/'test.c').write_text(TEST)
 subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror','-I/mnt/d/lab/HarmonyOSForMatebookego/references/L410-HarmonyOS-Adaptations/bluetooth',SOURCE,str(p/'test.c'),'-ldl','-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: missing transport rejects init; no success callback or fabricated HCI channel')
'''
if __name__=='__main__':
    payload='TEST='+repr(test)+'\nSOURCE='+repr('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/'+source.name)+'\n'+script
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60).returncode)

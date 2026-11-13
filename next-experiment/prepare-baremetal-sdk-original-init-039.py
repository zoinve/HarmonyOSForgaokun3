"""Add a bounded policy-authorized observer, preserving original init and service ownership."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-sdk-original-init-038.py'))
source=parent['source']
ping=(base/'baremetal-sdk-samgr-ping-030.h').read_text()
# Original SDK BinderInvoker::PingService uses this flag and the same PING code.
anchor='.target.handle = 0, .code = 0x5f504e47'
assert ping.count(anchor)==1
ping=ping.replace(anchor,anchor+', .flags = 0x200000')
ping=ping.replace('SELINUX030_','ORIGINAL_INIT039_')
observer=(base/'baremetal-sdk-manager-observer-039.h').read_text()
index=observer.index('static void manager_observer_039')
addition=observer[:index]+'\n#define require(ok, message) observer_require_039((ok), (message))\n'+ping+'\n#undef require\n'+observer[index:]
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,'#include <linux/android/binder.h>\n#include <time.h>\n'+addition+'\n'+anchor)
anchor='    char *const environment[] = '
assert source.count(anchor)==1
source=source.replace(anchor,'''    pid_t observer = fork();
    if (observer < 0) fail("fork bounded original-manager observer");
    if (!observer) manager_observer_039();
'''+anchor)
source=source.replace('ORIGINAL_INIT038_','ORIGINAL_INIT039_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-038','baremetal-sdk-original-init-039')
compile(payload,'original-init-039-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

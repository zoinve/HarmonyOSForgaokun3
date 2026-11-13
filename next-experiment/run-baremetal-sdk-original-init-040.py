"""Same original boot and policies; observer retries only transient device preparation denials."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-039.py')))['payload']
for old,new in [('original-init-qemu-039','original-init-qemu-040'),('original-init-039','original-init-040'),
                ('harmony-sdk-qemu039-','harmony-sdk-qemu040-'),('ORIGINAL_INIT039_','ORIGINAL_INIT040_')]:
    assert old in payload;payload=payload.replace(old,new)
compile(payload,'original-init-040-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)

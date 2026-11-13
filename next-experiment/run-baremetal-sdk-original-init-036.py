"""Same 035 boot settings; only the init fixture's device filesystem changes."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-035.py')))['payload']
for old,new in [('baremetal-sdk-original-init-qemu-035','baremetal-sdk-original-init-qemu-036'),
                ('baremetal-sdk-original-init-035','baremetal-sdk-original-init-036'),('ORIGINAL_INIT035_','ORIGINAL_INIT036_')]:
    assert old in payload;payload=payload.replace(old,new)
compile(payload,'original-init-036-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(r.returncode)

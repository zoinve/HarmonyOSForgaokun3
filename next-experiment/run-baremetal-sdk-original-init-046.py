"""Same original enforcing boot; new read-only reply metadata measurement."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-040.py')))['payload']
for old,new in [('original-init-qemu-040','original-init-qemu-046'),('original-init-040','original-init-046'),
                ('harmony-sdk-qemu040-','harmony-sdk-qemu046-'),('ORIGINAL_INIT040_','ORIGINAL_INIT046_')]:
    assert old in payload;payload=payload.replace(old,new)
compile(payload,'original-init-046-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)

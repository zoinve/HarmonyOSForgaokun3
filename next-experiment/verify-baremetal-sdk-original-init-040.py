"""Independent immutable artifact and actual observer-evidence verification for 040."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-sdk-original-init-039.py')))['payload']
payload=payload.replace('original-init-qemu-039','original-init-qemu-040').replace('original-init-039','original-init-040').replace('ORIGINAL_INIT039_','ORIGINAL_INIT040_')
compile(payload,'verify-original-init-040','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240)
    raise SystemExit(r.returncode)

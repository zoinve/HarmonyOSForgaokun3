"""Re-run the corrected continuous-mapping nested harness on unchanged kernel."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-004.py')))['source']
source=source.replace('baremetal-identity-qemu-004','baremetal-identity-qemu-005')
source=source.replace('baremetal-identity-nested-004','baremetal-identity-nested-005')
source=source.replace('IDENTITY004_','IDENTITY005_')
compile(source,'qemu-nested-005','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

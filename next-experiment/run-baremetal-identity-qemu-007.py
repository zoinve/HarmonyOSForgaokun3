"""Run original SDK APIs with its documented device-node policy, unchanged kernel."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-006.py')))['source']
source=source.replace('baremetal-identity-qemu-006','baremetal-identity-qemu-007')
source=source.replace('baremetal-identity-sdk-006','baremetal-identity-sdk-007')
source=source.replace('IDENTITY006_','IDENTITY007_').replace('SDK006_','SDK007_')
compile(source,'qemu-sdk-007','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

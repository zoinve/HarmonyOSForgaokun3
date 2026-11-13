"""Use unchanged 002 test kernel and the fresh 011 original SDK transaction init."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-010.py')))['source']
source=source.replace('baremetal-identity-qemu-010','baremetal-identity-qemu-011')
source=source.replace('baremetal-identity-ipc-transactions-010','baremetal-identity-ipc-transactions-011')
for old,new in [('IDENTITY010_','IDENTITY011_'),('SDK010_','SDK011_'),('IPC010_','IPC011_')]:
    source=source.replace(old,new)
compile(source,'qemu-ipc-transactions-011','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

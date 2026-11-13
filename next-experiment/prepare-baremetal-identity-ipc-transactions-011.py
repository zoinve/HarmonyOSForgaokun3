"""Retain failed 010 evidence; mark its deliberately retained mapping as used."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-identity-ipc-transactions-010.py')))
source=parent['source']
anchor='    /* Mapping retained for the original SDK transaction below. */'
assert source.count(anchor)==1
source=source.replace(anchor,'    (void)mapping; /* Caller retains mapping for the original SDK transaction. */')
source=source.replace('IDENTITY010_','IDENTITY011_').replace('IPC010_','IPC011_')
sdk_source=parent['sdk_source'].replace('SDK010_','SDK011_').replace('IPC010_','IPC011_')
payload=parent['payload'];payload=payload[payload.index('\nfrom pathlib import Path')+1:]
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload
payload=payload.replace('baremetal-identity-ipc-transactions-010','baremetal-identity-ipc-transactions-011')
compile(payload,'prepare-ipc-transactions-011','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=300)
    raise SystemExit(result.returncode)

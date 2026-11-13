"""Original SDK transaction regression with the unchanged diskless test kernel."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-009.py')))['source']
source=source.replace('baremetal-identity-qemu-009','baremetal-identity-qemu-010')
source=source.replace('baremetal-identity-native-read-009','baremetal-identity-ipc-transactions-010')
for old,new in [('IDENTITY009_','IDENTITY010_'),('SDK009_','SDK010_'),('IPC009_','IPC010_')]:
    source=source.replace(old,new)
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'IPC010_TRANSACTION_PASS original_parcel=1 original_invoker=1 authentic_sender_checked=1 reply_verified=1' in log\n report['original_sdk_transaction_verified']=True\n"+anchor)
compile(source,'qemu-ipc-transactions-010','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

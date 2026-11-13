"""Run original SDK nested callback against unchanged 002 test kernel, no disks."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-011.py')))['source']
source=source.replace('baremetal-identity-qemu-011','baremetal-identity-qemu-012')
source=source.replace('baremetal-identity-ipc-transactions-011','baremetal-identity-ipc-callback-012')
for old,new in [('IDENTITY011_','IDENTITY012_'),('SDK011_','SDK012_'),('IPC011_','IPC012_')]:
    source=source.replace(old,new)
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'IPC012_CALLBACK_PASS original_dispatch=1 calling_full_token=1 first_full_token=1 pid_uid=1 self_preserved=1' in log\n assert 'IPC012_CALLBACK_RESTORE_PASS outside_context=1 full_tokens=1 pid_uid=1' in log\n report['original_sdk_nested_callback_verified']=True\n"+anchor)
compile(source,'qemu-ipc-callback-012','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

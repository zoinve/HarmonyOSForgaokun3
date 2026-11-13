"""Verify the native read probe in diskless QEMU before considering a board boot."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-008.py')))['source']
source=source.replace('baremetal-identity-qemu-008','baremetal-identity-qemu-009')
source=source.replace('baremetal-identity-connector-008','baremetal-identity-native-read-009')
for old,new in [('IDENTITY008_','IDENTITY009_'),('SDK008_','SDK009_'),('IPC008_','IPC009_')]:source=source.replace(old,new)
assert source.count("['dev','proc','sys']")==1
source=source.replace("['dev','proc','sys']","['dev','proc','sys','run']")
assert source.count('harmony.identity_test=1 panic=-1')==1
source=source.replace('harmony.identity_test=1 panic=-1','harmony.identity_test=1 harmony.diag=1 panic=-1')
anchor=" report['runtime_verified']=True";assert source.count(anchor)==1
source=source.replace(anchor," assert 'NATIVE_IDENTITY_READ001_PASS protocol=8 features=5' in log and 'NATIVE_IDENTITY_READ001_FAIL' not in log\n report['diagnostic_read_probe_verified']=True\n report['diagnostic_read_result']=[line for line in log.splitlines() if 'NATIVE_IDENTITY_READ001_' in line]\n"+anchor)
compile(source,'qemu-native-read-009','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

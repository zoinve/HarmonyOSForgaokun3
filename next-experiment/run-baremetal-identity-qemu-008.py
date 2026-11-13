"""Add the unmodified SDK BinderConnector dependency closure to diskless QEMU."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-007.py')))['source']
source=source.replace('baremetal-identity-qemu-007','baremetal-identity-qemu-008')
source=source.replace('baremetal-identity-sdk-007','baremetal-identity-connector-008')
source=source.replace('IDENTITY007_','IDENTITY008_').replace('SDK007_','SDK008_')
anchor="  assert row['name'] in ['sdk/loader','sdk/probe','sdk/libtokensetproc_shared.z.so','sdk/libsec_shared.z.so']"
assert source.count(anchor)==1
source=source.replace(anchor,"  assert row['name'].startswith('sdk/') and '/' not in row['name'][4:] and '..' not in row['name'][4:]")
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'IPC008_PASS protocol_accepted=1' in log and 'IPC008_DLOPEN' not in log\n report['original_sdk_connector_verified']=True\n report['connector_probe_result']=[line for line in log.splitlines() if 'IPC008_' in line]\n"+anchor)
compile(source,'qemu-connector-008','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

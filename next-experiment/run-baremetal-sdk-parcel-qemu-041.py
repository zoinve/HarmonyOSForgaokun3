"""Encoding-only SDK regression on unchanged diskless 002 kernel, not service authorization."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-012.py')))['source']
source=source.replace('baremetal-identity-qemu-012','baremetal-sdk-parcel-qemu-041')
source=source.replace('baremetal-identity-ipc-callback-012','baremetal-sdk-parcel-041')
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'PARCEL041_PASS original_proxy_descriptor=1 original_parcel_encoder=1 service_query_not_tested=1' in log\n report['original_parcel_encoding_observed']=True\n report['service_query_verified']=False\n"+anchor)
compile(source,'parcel-qemu-041','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(r.returncode)

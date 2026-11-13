"""Run original SDK token APIs in the isolated kernel, never on the live board."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-005.py')))['source']
source=source.replace('baremetal-identity-qemu-005','baremetal-identity-qemu-006')
source=source.replace('baremetal-identity-nested-005','baremetal-identity-sdk-006')
source=source.replace('IDENTITY005_','IDENTITY006_')
anchor=" entry('init',stat.S_IFREG|0o755,probe.read_bytes());entry('TRAILER!!!',0)"
assert source.count(anchor)==1
source=source.replace(anchor,''' entry('init',stat.S_IFREG|0o755,probe.read_bytes())
 entry('sdk',stat.S_IFDIR|0o755)
 for row in probe_result['ram_files']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
  assert row['name'] in ['sdk/loader','sdk/probe','sdk/libtokensetproc_shared.z.so','sdk/libsec_shared.z.so']
  entry(row['name'],stat.S_IFREG|0o755,p.read_bytes())
 entry('sdk/libc.so',stat.S_IFLNK|0o777,b'loader')
 entry('TRAILER!!!',0)''')
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'SDK006_PASS checks=' in log and 'SDK006_FAIL' not in log\n report['original_sdk_api_verified']=True\n report['sdk_probe_result']=[line for line in log.splitlines() if 'SDK006_' in line]\n"+anchor)
compile(source,'qemu-sdk-006','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

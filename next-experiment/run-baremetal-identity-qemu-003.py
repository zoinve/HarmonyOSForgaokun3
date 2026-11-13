"""Run the transaction init with the verified test-only 002 kernel; no rebuild/install."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-002.py')))['payload']
source=source.replace("reports/baremetal-identity-qemu-002'","reports/baremetal-identity-qemu-003'")
source=source.replace("work=root/'baremetal-identity-qemu-002'","work=root/'baremetal-identity-qemu-003'")
start=source.index('work.mkdir();local.mkdir();build=')
end=source.index('env=dict(os.environ',start)
source=source[:start]+'''previous=root/'baremetal-identity-qemu-002'
assert json.loads((previous/'result.json').read_text())['runtime_verified']
work.mkdir();local.mkdir();build=previous/'out'
native_config=sha(candidate/'out/.config');test_config=sha(build/'.config');test_kernel=sha(build/'arch/arm64/boot/Image')
probe_result=json.loads((root/'baremetal-identity-transactions-003/result.json').read_text())
probe=Path(probe_result['path']);assert sha(probe)==probe_result['sha256'] and probe.stat().st_size==probe_result['bytes']
'''+source[end:]
start=source.index(" run([str(src/'scripts/config')")
end=source.index(' # Deterministic newc archive',start)
source=source[:start]+source[end:]
source=source.replace('transactions_tested=False','transactions_tested=True,nested_transactions_tested=False')
source=source.replace('IDENTITY002_','IDENTITY003_')
assert source.count(" report['runtime_verified']=True")==1
source=source.replace(" report['runtime_verified']=True",''' for iteration in range(3):
  assert f'IDENTITY003_TRANSACTION iteration={iteration} oneway={int(iteration==2)} verified=1' in log
 report['test_kernel_sha256']=test_kernel
 report['test_kernel_and_config_unchanged']=sha(build/'arch/arm64/boot/Image')==test_kernel and sha(build/'.config')==test_config
 assert report['test_kernel_and_config_unchanged']
 report['runtime_verified']=True''')
compile(source,'qemu-003-payload','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

"""Run real nested Binder calls with the already-verified isolated test kernel."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-identity-qemu-003.py')))['source']
source=source.replace('baremetal-identity-qemu-003','baremetal-identity-qemu-004')
source=source.replace('baremetal-identity-transactions-003','baremetal-identity-nested-004')
source=source.replace('IDENTITY003_','IDENTITY004_')
source=source.replace('nested_transactions_tested=False','nested_transactions_tested=True')
anchor=" report['runtime_verified']=True"
assert source.count(anchor)==1
source=source.replace(anchor," assert 'IDENTITY004_NESTED callback=1 reply_identity_changed=1 self_tokens_preserved=1 verified=1' in log\n"+anchor)
compile(source,'qemu-nested-004','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(result.returncode)

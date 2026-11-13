"""Fix only the diskless missing-GPU fixture: provide an empty bundle bind source."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-mesa-qemu-048.py')))['payload']
payload=payload.replace('baremetal-mesa-qemu-048','baremetal-mesa-qemu-049').replace('NATIVE_MESA048_','NATIVE_MESA049_')
anchor="for name in ['dev','proc','sys','run']:entry(name,stat.S_IFDIR|0o755)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"for name in ['dev','proc','sys','run','opt','opt/native-mesa-001']:entry(name,stat.S_IFDIR|0o755)")
compile(payload,'mesa049-corrected-empty-bundle-fixture','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

"""Fresh encoding test; preserve failed 041 and its overly restrictive pointer guard."""
from pathlib import Path
import runpy
import subprocess

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-parcel-qemu-041.py')))['source']
for old,new in [('baremetal-sdk-parcel-qemu-041','baremetal-sdk-parcel-qemu-042'),
                ('baremetal-sdk-parcel-041','baremetal-sdk-parcel-042'),('PARCEL041_','PARCEL042_')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'parcel-qemu-042','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=source,text=True,timeout=220)
    raise SystemExit(r.returncode)

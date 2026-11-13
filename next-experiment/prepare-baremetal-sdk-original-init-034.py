"""Build only the guarded handoff helper; original policy remains unmodified."""
from pathlib import Path
import runpy
import subprocess

source=Path(__file__).with_name('baremetal-sdk-original-init-034.c').read_text()
parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-selinux-load-013.py')))['payload']
payload='source='+repr(source)+'\n'+parent[parent.index('\nfrom pathlib import Path')+1:]
assert 'baremetal-selinux-load-013' in payload
payload=payload.replace('baremetal-selinux-load-013','baremetal-sdk-original-init-034')
compile(payload,'original-init-034-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

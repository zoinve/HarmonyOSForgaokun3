"""Package native-fence evidence probe separately, retaining all previous bundles."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
out=base.parent/'reports/baremetal-freedreno-fence-package-001'
old=runpy.run_path(str(base/'package-baremetal-freedreno-dmabuf-001.py'),run_name='payload_only')['payload']
source=runpy.run_path(str(base/'baremetal-freedreno-fence-probe-001.py'))['build_source']()
payload='source='+repr(source)+'\n'+old[old.index('header='):]
payload=payload.replace('baremetal-freedreno-dmabuf-package-001','baremetal-freedreno-fence-package-001')
payload=payload.replace("work=root/'baremetal-freedreno-dmabuf-001'","work=root/'baremetal-freedreno-fence-001'")
compile(payload,'fence-package-001','exec')

if __name__=='__main__':
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)

"""Fresh package after checking the unused reference constant with a static assertion."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'package-baremetal-composer-probe-002.py'))['payload']
for old,new in [('baremetal-composer-probe-package-002','baremetal-composer-probe-package-003'),
                ("work=root/'baremetal-composer-probe-002'","work=root/'baremetal-composer-probe-003'")]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'composer-probe003-package','exec')
if __name__=='__main__':
    out=base.parent/'reports/baremetal-composer-probe-package-003'
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=180)

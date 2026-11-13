"""Preserve failed001 packaging; carry forward its omitted private protocol-header literal."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'package-baremetal-composer-probe-001.py'))
payload='ipc_header='+repr(parent['namespace']['ipc_header'])+'\n'+parent['payload']
payload=payload.replace('baremetal-composer-probe-package-001','baremetal-composer-probe-package-002').replace("work=root/'baremetal-composer-probe-001'","work=root/'baremetal-composer-probe-002'")
compile(payload,'composer-probe002-package','exec')
if __name__=='__main__':
    out=base.parent/'reports/baremetal-composer-probe-package-002'
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=180)

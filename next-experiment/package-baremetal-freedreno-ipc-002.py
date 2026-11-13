"""Fresh build after replacing the SDK's sign-warning CMSG_NXTHDR macro with bounded iteration."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
payload=runpy.run_path(str(base/'package-baremetal-freedreno-ipc-001.py'))['payload']
for old,new in [('baremetal-freedreno-ipc-package-001','baremetal-freedreno-ipc-package-002'),
                ("work=root/'baremetal-freedreno-ipc-001'","work=root/'baremetal-freedreno-ipc-002'"),
                ('IPC001_','IPC002_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'ipc-probe002-package','exec')
if __name__=='__main__':
    out=base.parent/'reports/baremetal-freedreno-ipc-package-002'
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)

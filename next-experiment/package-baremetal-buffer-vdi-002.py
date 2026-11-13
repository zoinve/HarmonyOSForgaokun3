"""Fresh package: reference default-method warning compatibility and correct uint32 log format."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('package-baremetal-buffer-vdi-001.py')))
old=parent['vdi'];assert old.count('usage=0x%llx expected=%zu')==1
vdi=old.replace('usage=0x%llx expected=%zu','usage=0x%llx expected=%u')
payload=parent['payload']
anchor='vdi='+repr(old)+'\n';assert payload.startswith(anchor)
payload='vdi='+repr(vdi)+'\n'+payload[len(anchor):]
assert "'-Wall','-Wextra','-Werror'" in payload
payload=payload.replace("'-Wall','-Wextra','-Werror'","'-Wall','-Wextra','-Werror','-Wno-unused-parameter'")
payload=payload.replace('baremetal-buffer-vdi-001','baremetal-buffer-vdi-002').replace('baremetal-buffer-vdi-package-001','baremetal-buffer-vdi-package-002')
payload=payload.replace('libnative-buffer-vdi-001.so','libnative-buffer-vdi-002.so').replace('NATIVE_ALLOC001_','NATIVE_ALLOC002_')
compile(payload,'native-buffer-vdi-package002','exec')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)

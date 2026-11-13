"""Independently prove exactly one private probe differs from native candidate011."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-diagnostic-init-011.py')))['payload']
payload=payload.replace('baremetal-diagnostic-init-011','baremetal-diagnostic-init-014')
payload=payload.replace('baremetal-freedreno-fence-package-002','baremetal-freedreno-ipc-package-002')
payload=payload.replace('baremetal-diagnostic-init-010/result.json','baremetal-diagnostic-init-011/result.json')
start=payload.index("expected=sorted('opt/native-mesa-001/lib/'")
end=payload.index('assert changed==expected,changed',start)
payload=payload[:start]+"expected=['opt/native-mesa-001/probe']\n"+payload[end:]
payload=payload.replace('only_five_mesa_libraries_changed=True','only_cross_process_probe_changed=True')
payload=payload.replace('all_other_010_records_unchanged=True','all_other_011_records_unchanged=True')
compile(payload,'native014-independent','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120)
    raise SystemExit(r.returncode)

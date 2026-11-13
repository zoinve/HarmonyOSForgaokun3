"""Keep original boot protection; report identity diagnostics without claiming query authorization."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-043.py')))['payload']
for old,new in [('original-init-qemu-043','original-init-qemu-044'),('original-init-043','original-init-044'),
                ('harmony-sdk-qemu043-','harmony-sdk-qemu044-'),('ORIGINAL_INIT043_','ORIGINAL_INIT044_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
anchor="  report['sa_list_semantically_verified']=False"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"  report['genuine_list_terminal_rejection_observed']='ORIGINAL_INIT044_MANAGER_LIST_REJECTED terminal=1 enforcing=1' in serial.read_text(errors='replace')\n"+anchor)
compile(payload,'original-init-044-run','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)

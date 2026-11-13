"""Fresh candidate after 012 exposed the allocator manifest's different closure field."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-diagnostic-init-012.py')))
source=parent['source']
payload=parent['payload'].replace('baremetal-diagnostic-init-012','baremetal-diagnostic-init-013')
anchor="manifest['all_strong_dynamic_symbols_resolved']"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"manifest['all_needed_libraries_present']")
compile(payload,'prepare-native-allocator013','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

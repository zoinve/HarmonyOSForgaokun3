"""Independent full-record audit; only private probe and extracted-method bridge change."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-diagnostic-init-014.py')))['payload']
payload=payload.replace('baremetal-diagnostic-init-014','baremetal-diagnostic-init-015')
payload=payload.replace('baremetal-freedreno-ipc-package-002','baremetal-composer-probe-package-003')
payload=payload.replace('baremetal-diagnostic-init-011/result.json','baremetal-diagnostic-init-014/result.json')
assert 'len(expected)==17' in payload
payload=payload.replace('len(expected)==17','len(expected)==18')
assert 'assert previous.keys()==new.keys()' in payload
payload=payload.replace('assert previous.keys()==new.keys()',"assert previous.keys() <= new.keys()\nassert sorted(new.keys()-previous.keys())==['opt/native-mesa-001/lib/libcomposer-methods-001.so']")
payload=payload.replace('only_cross_process_probe_changed=True','only_private_composer_method_payload_changed=True')
payload=payload.replace('all_other_011_records_unchanged=True','all_other_014_records_unchanged=True,extracted_methods_only=True,full_composer_hdi_verified=False')
compile(payload,'native015-independent','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120)
    raise SystemExit(r.returncode)

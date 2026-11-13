"""Independently verify every allocator archive record and unchanged native boot machinery."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-diagnostic-init-010.py')))['payload']
payload=payload.replace('baremetal-diagnostic-init-010','baremetal-diagnostic-init-013')
payload=payload.replace('baremetal-freedreno-fence-package-001','baremetal-buffer-vdi-package-004')
assert payload.count('len(expected)==17')==1
payload=payload.replace('len(expected)==17','len(expected)==42')
anchor="out.write_text(json.dumps(result,indent=2)+'\\n');"
assert payload.count(anchor)==1
extra=r'''
previous_meta=json.loads((project/'reports/baremetal-diagnostic-init-011/result.json').read_text())
previous_path=Path(previous_meta['archive'])
assert sha(previous_path)==previous_meta['archive_sha256']
previous=archive(previous_path)
assert previous.keys() <= new.keys()
changed=sorted(name for name in previous if previous[name]!=new[name])
assert changed==['opt/native-mesa-001/probe'],changed
added=sorted(new.keys()-previous.keys())
assert len(added)==25 and all(name.startswith('opt/native-mesa-001/lib/') for name in added)
assert new['init']==previous['init'] and new['bin/native-mesa-launcher-001']==previous['bin/native-mesa-launcher-001']
assert len(manifest['files'])==34
assert sha(project/'reports/baremetal-buffer-vdi-package-004/bundle.tar.gz')=='c8e920ccf777775986771d04b586afeffe995ca882869f9ae09b961c725ed084'
verified=json.loads((project/'reports/baremetal-buffer-vdi-run-004/independent-verification.json').read_text())
assert verified['original_sdk_handle_abi_verified'] and verified['cpu_gpu_coherency_with_glFinish_verified']
result.update(only_private_allocator_payload_changed=True,changed_archive_entries=changed,
              added_archive_entries=added,all_other_011_records_unchanged=True,
              all_34_allocator_files_verified=True,native_allocator_gpu_execution_verified=False)
'''
payload=payload.replace(anchor,extra+'\n'+anchor)
compile(payload,'independent-native-allocator013','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120)
    raise SystemExit(r.returncode)

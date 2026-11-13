"""Native extracted-method probe only; no full composer, HDI or display initialization."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-diagnostic-init-014.py')))
source=parent['source']
payload=parent['payload'].replace('baremetal-diagnostic-init-014','baremetal-diagnostic-init-015')
payload=payload.replace('baremetal-freedreno-ipc-package-002','baremetal-composer-probe-package-003')
payload=payload.replace('baremetal-freedreno-ipc-run-002','baremetal-composer-probe-run-003')
payload=payload.replace("len(manifest['files'])==9","len(manifest['files'])==10")
guard="assert gpu_verified['cross_process_gpu_execution_verified'] and gpu_verified['distinct_exec_consumer_verified'] and len(manifest['files'])==10"
assert payload.count(guard)==1
payload=payload.replace(guard,guard+"\nassert gpu_verified['extracted_composer_methods_verified'] and not gpu_verified['full_composer_hdi_verified']\nassert manifest['extracted_methods_only'] and not manifest['full_hdi_abi_verified']")
start=payload.index("old011=root/'baremetal-diagnostic-init-011'")
end=payload.index("\n(work/'result.json').write_text",start)
payload=payload[:start]+r'''
previous=root/'baremetal-diagnostic-init-014'
previous_meta=json.loads((previous/'result.json').read_text())
assert sha(previous/'diagnostic-init.cpio.gz')==previous_meta['archive_sha256']
prior=contents_of_archive(previous/'diagnostic-init.cpio.gz')
current=contents_of_archive(work/'diagnostic-init.cpio.gz')
assert prior.keys() <= current.keys()
changed=sorted(name for name in prior if prior[name]!=current[name])
added=sorted(current.keys()-prior.keys())
assert changed==['opt/native-mesa-001/probe'],changed
assert added==['opt/native-mesa-001/lib/libcomposer-methods-001.so'],added
assert d['binary_sha256']==previous_meta['binary_sha256']
assert d['launcher_sha256']==previous_meta['launcher_sha256']
d.update(compared_with_candidate014=True,changed_archive_entries=changed,
         added_archive_entries=added,only_private_composer_method_payload_changed=True,
         extracted_methods_only=True,full_composer_hdi_verified=False,
         native_composer_method_gpu_execution_verified=False)
'''+payload[end:]
compile(payload,'native-composer-method015-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

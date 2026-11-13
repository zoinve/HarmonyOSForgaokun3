"""Fresh native cross-process probe: only probe bytes change versus proven candidate011."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-diagnostic-init-011.py')))
source=parent['source']
payload=parent['payload'].replace('baremetal-diagnostic-init-011','baremetal-diagnostic-init-014')
payload=payload.replace('baremetal-freedreno-fence-package-002','baremetal-freedreno-ipc-package-002')
payload=payload.replace('baremetal-freedreno-fence-run-002','baremetal-freedreno-ipc-run-002')
assert "assert gpu_verified and manifest['probe_reused_unchanged']" in payload
payload=payload.replace("assert gpu_verified and manifest['probe_reused_unchanged']",
 "assert gpu_verified['cross_process_gpu_execution_verified'] and gpu_verified['distinct_exec_consumer_verified'] and len(manifest['files'])==9")
start=payload.index("old_entries=contents_of_archive(old010/'diagnostic-init.cpio.gz')")
end=payload.index("\n(work/'result.json').write_text",start)
payload=payload[:start]+r'''
old011=root/'baremetal-diagnostic-init-011'
old011_result=json.loads((old011/'result.json').read_text())
assert sha(old011/'diagnostic-init.cpio.gz')==old011_result['archive_sha256']
old_entries=contents_of_archive(old011/'diagnostic-init.cpio.gz')
new_entries=contents_of_archive(work/'diagnostic-init.cpio.gz')
assert old_entries.keys()==new_entries.keys()
changed=sorted(name for name in old_entries if old_entries[name]!=new_entries[name])
assert changed==['opt/native-mesa-001/probe'],changed
assert d['binary_sha256']==old011_result['binary_sha256']
d.update(compared_with_candidate011=True,changed_archive_entries=changed,
         only_cross_process_probe_changed=True,launcher_reused_unchanged=True,
         native_gpu_execution_verified=False)
'''+payload[end:]
compile(payload,'native-ipc014-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

"""Private allocator payload regression; keep the proven native diagnostic and launcher exact."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-diagnostic-init-011.py')))
source=parent['source']
payload=parent['payload'].replace('baremetal-diagnostic-init-011','baremetal-diagnostic-init-012')
assert payload.count('baremetal-freedreno-fence-package-002')==2
payload=payload.replace('baremetal-freedreno-fence-package-002','baremetal-buffer-vdi-package-004')
payload=payload.replace("len(manifest['files'])==9","len(manifest['files'])==34")
payload=payload.replace('baremetal-freedreno-fence-run-002/independent-verification.json',
                        'baremetal-buffer-vdi-run-004/independent-verification.json')
anchor="assert gpu_verified and manifest['probe_reused_unchanged']"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"assert gpu_verified['all_34_archive_and_remote_files_verified'] and gpu_verified['original_sdk_handle_abi_verified'] and gpu_verified['cpu_gpu_coherency_with_glFinish_verified'] and manifest['reference_files_unchanged']")
start=payload.index('def contents_of_archive(path):')
end=payload.index("(work/'result.json').write_text",start)
parser=parent['comparison'].split('old_entries=')[0]
comparison=parser+r'''
old011=root/'baremetal-diagnostic-init-011'
previous=json.loads((old011/'result.json').read_text())
assert sha(old011/'diagnostic-init.cpio.gz')==previous['archive_sha256']
old_entries=contents_of_archive(old011/'diagnostic-init.cpio.gz')
new_entries=contents_of_archive(work/'diagnostic-init.cpio.gz')
assert old_entries.keys() <= new_entries.keys()
changed=sorted(name for name in old_entries if old_entries[name]!=new_entries[name])
assert changed==['opt/native-mesa-001/probe'],changed
added=sorted(new_entries.keys()-old_entries.keys())
assert len(added)==25 and all(name.startswith('opt/native-mesa-001/lib/') for name in added),added
assert d['binary_sha256']==previous['binary_sha256']
assert sha(work/'mesa-launcher')==previous['launcher_sha256']
d.update(compared_with_candidate011=True,changed_archive_entries=changed,added_archive_entries=added,
    only_private_allocator_payload_changed=True,launcher_reused_unchanged=True,
    init_reused_byte_identical=True,native_allocator_gpu_execution_verified=False)
'''
payload=payload[:start]+comparison+'\n'+payload[end:]
compile(payload,'prepare-native-allocator012','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)

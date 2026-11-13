"""Independent extracted-method evidence and unchanged Ubuntu-state verification."""
from pathlib import Path
import runpy

base=Path(__file__).resolve().parent
source=runpy.run_path(str(base/'verify-baremetal-freedreno-ipc-002.py'))['source']
for old,new in [('baremetal-freedreno-ipc-package-002','baremetal-composer-probe-package-003'),
                ('baremetal-freedreno-ipc-run-002','baremetal-composer-probe-run-003'),
                ('IPC002_','COMPOSER001_'),('len(new)==9','len(new)==10'),
                ('fence_poll=1','reference_fence_wait_success=1'),
                ('all_nine_archive_and_remote_files_verified','all_ten_archive_and_remote_files_verified')]:
    assert old in source,old
    source=source.replace(old,new)
anchor="assert run['cross_process_gpu_execution_verified']"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\nassert run['extracted_composer_contract_gpu_verified'] and not run['full_composer_hdi_verified']\nassert 'COMPOSER001_CONTRACT actual_reference_methods=1 caller_fds_closed=1 held_fd_closed=1 no_init_display=1 no_commit=1' in run['run']['stdout']")
source=source.replace('desktop_verified=False)','desktop_verified=False,extracted_composer_methods_verified=True,full_composer_hdi_verified=False)')
compile(source,'composer003-independent','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

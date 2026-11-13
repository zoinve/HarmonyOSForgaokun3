"""Stage independently verified cross-process-only payload, without EFI changes."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('stage-baremetal-identity-diagnostic-010.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-identity-diagnostic-010','baremetal-identity-diagnostic-014'),
                ('native-identity-diagnostic-010','native-identity-diagnostic-014'),
                ('baremetal-diagnostic-init-010','baremetal-diagnostic-init-014')]:
    assert old in source
    source=source.replace(old,new)
anchor="assert archive_check['binary_helper_kernel_dtb_hashes_verified']"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\nassert archive_check['only_cross_process_probe_changed'] and archive_check['all_other_011_records_unchanged']")
compile(source,'stage014','exec')
if __name__=='__main__':exec(compile(source,'stage014','exec'),{'__file__':__file__,'__name__':'__main__'})

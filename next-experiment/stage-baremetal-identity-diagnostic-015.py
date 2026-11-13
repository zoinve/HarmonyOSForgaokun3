"""Stage verified private composer-method payload; do not touch EFI."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('stage-baremetal-identity-diagnostic-010.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-identity-diagnostic-010','baremetal-identity-diagnostic-015'),
                ('native-identity-diagnostic-010','native-identity-diagnostic-015'),
                ('baremetal-diagnostic-init-010','baremetal-diagnostic-init-015')]:
    assert old in source,old
    source=source.replace(old,new)
anchor="assert archive_check['binary_helper_kernel_dtb_hashes_verified']"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\nassert archive_check['only_private_composer_method_payload_changed'] and archive_check['all_other_014_records_unchanged']")
compile(source,'stage015','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

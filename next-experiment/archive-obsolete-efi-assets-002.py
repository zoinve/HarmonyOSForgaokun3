"""Archive only three unreferenced candidate005 EFI assets; retain every experiment byte."""
from pathlib import Path

source=Path(__file__).with_name('archive-obsolete-efi-assets-001.py').read_text()
for old,new in [('baremetal-efi-assets-archive-001','baremetal-efi-assets-archive-002'),
                ('baremetal-efi-space-audit-001','baremetal-efi-space-audit-002'),
                ("[('001','004')]","[('002','005')]"),
                ('harmony-native-diag-004','harmony-native-diag-005'),
                ('efi-assets-archive-001','efi-assets-archive-002')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'archive005-adapter','exec')
if __name__=='__main__':
    exec(compile(source,'archive005-adapter','exec'),{'__file__':__file__,'__name__':'__main__'})

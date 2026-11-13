"""Corrected006 directory selection; failed003 retained unchanged."""
from pathlib import Path
source=Path(__file__).with_name('archive-obsolete-efi-assets-001.py').read_text()
source=source.replace('baremetal-efi-space-audit-001','baremetal-efi-space-audit-003').replace('efi-assets-archive-001','efi-assets-archive-004')
assert "[('001','004')]" in source
source=source.replace("[('001','004')]","[('003','006')]").replace('harmony-native-diag-004','harmony-native-diag-006')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

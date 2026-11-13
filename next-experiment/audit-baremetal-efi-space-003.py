"""Fresh read-only candidate015 capacity and obsolete-asset inventory."""
from pathlib import Path

source=Path(__file__).with_name('audit-baremetal-efi-space-002.py').read_text()
source=source.replace('baremetal-efi-space-audit-002','baremetal-efi-space-audit-003')
source=source.replace("assert not (esp/'harmony-native-diag-014').exists()", "assert not (esp/'harmony-native-diag-015').exists()")
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

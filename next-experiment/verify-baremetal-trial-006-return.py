"""Verify006 raw evidence, consumed009 entry and already-off Ubuntu state read-only."""
from pathlib import Path

source=Path(__file__).with_name('verify-baremetal-trial-005-return.py').read_text()
for old,new in [('baremetal-native-trial-005','baremetal-native-trial-006'),
                ('boot-entry-install-005','boot-entry-install-006'),
                ('harmony-native-diag-008','harmony-native-diag-009')]:
    assert old in source,old;source=source.replace(old,new)
compile(source,'verify006','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

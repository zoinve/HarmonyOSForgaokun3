"""One new identity-kernel diagnostic boot with immediate SSH observation and collection."""
from pathlib import Path

source=Path(__file__).with_name('run-baremetal-diagnostic-trial-002.py').read_text()
for old,new in [
    ('baremetal-native-trial-002','baremetal-native-trial-005'),
    ('baremetal-boot-entry-installed-002','baremetal-boot-entry-installed-005'),
    ('boot-entry-install-002','boot-entry-install-005'),
    ('native-trial-002','native-trial-005'),
    ('harmony-native-diag-005','harmony-native-diag-008'),
]:
    assert old in source,old;source=source.replace(old,new)
compile(source,'trial005-launcher','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

"""One009 native diagnostic boot, immediate SSH return checks, automatic raw collection."""
from pathlib import Path

source=Path(__file__).with_name('run-baremetal-diagnostic-trial-002.py').read_text()
for old,new in [
    ('baremetal-native-trial-002','baremetal-native-trial-006'),
    ('baremetal-boot-entry-installed-002','baremetal-boot-entry-installed-006'),
    ('boot-entry-install-002','boot-entry-install-006'),
    ('native-trial-002','native-trial-006'),
    ('harmony-native-diag-005','harmony-native-diag-009'),
]:
    assert old in source,old;source=source.replace(old,new)
compile(source,'trial006-launcher','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

"""Verify trial009 raw hashes and Ubuntu state; refuse all display setters."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-trial-008-return.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-008','baremetal-native-trial-009'),
                ('boot-entry-install-008','boot-entry-install-009'),
                ('harmony-native-diag-011','harmony-native-diag-013')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'verify009','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

"""Select 011 once, observe SSH immediately, collect only after verified Ubuntu return."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-diagnostic-trial-007.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-007','baremetal-native-trial-008'),
                ('baremetal-boot-entry-installed-007','baremetal-boot-entry-installed-008'),
                ('boot-entry-install-007','boot-entry-install-008'),
                ('native-trial-007','native-trial-008'),('harmony-native-diag-010','harmony-native-diag-011')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'trial008','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

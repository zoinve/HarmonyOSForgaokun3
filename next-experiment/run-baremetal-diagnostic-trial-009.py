"""Select013 once, reconnect immediately and collect only after verified Ubuntu return."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-diagnostic-trial-008.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-008','baremetal-native-trial-009'),
                ('baremetal-boot-entry-installed-008','baremetal-boot-entry-installed-009'),
                ('boot-entry-install-008','boot-entry-install-009'),
                ('native-trial-008','native-trial-009'),('harmony-native-diag-011','harmony-native-diag-013')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'trial009','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

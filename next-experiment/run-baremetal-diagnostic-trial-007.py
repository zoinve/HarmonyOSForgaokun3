"""Select010 once, immediately reconnect SSH, collect raw logs after verified Ubuntu return."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-diagnostic-trial-006.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-006','baremetal-native-trial-007'),
                ('baremetal-boot-entry-installed-006','baremetal-boot-entry-installed-007'),
                ('boot-entry-install-006','boot-entry-install-007'),
                ('native-trial-006','native-trial-007'),('harmony-native-diag-009','harmony-native-diag-010')]:
    assert old in source,old;source=source.replace(old,new)
compile(source,'trial007-launcher','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

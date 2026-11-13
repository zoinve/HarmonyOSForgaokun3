"""One014 cross-process GPU trial, immediate SSH and verified Ubuntu collection."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-diagnostic-trial-010.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-010','baremetal-native-trial-011'),
                ('baremetal-boot-entry-installed-010','baremetal-boot-entry-installed-011'),
                ('boot-entry-install-010','boot-entry-install-011'),('native-trial-010','native-trial-011'),
                ('harmony-native-diag-013','harmony-native-diag-014')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'trial011','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

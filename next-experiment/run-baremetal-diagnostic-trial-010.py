"""One013 native allocator trial, immediate SSH and confirmed Ubuntu collection."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-diagnostic-trial-009.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-009','baremetal-native-trial-010'),
                ('baremetal-boot-entry-installed-009','baremetal-boot-entry-installed-010'),
                ('boot-entry-install-009','boot-entry-install-010'),('native-trial-009','native-trial-010')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'trial010','exec')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

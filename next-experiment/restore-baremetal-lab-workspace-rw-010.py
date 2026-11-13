"""Preserve all 302 trial010 raw logs when restoring only the lab preparation mount."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('restore-baremetal-lab-workspace-rw-009.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-008-collected','baremetal-native-trial-010-collected'),
                ('baremetal-lab-workspace-rw-009.json','baremetal-lab-workspace-rw-010.json'),
                ('assert len(files) == 264','assert len(files) == 302')]:
    assert source.count(old)==1
    source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,'restore-lab-rw010','exec'))

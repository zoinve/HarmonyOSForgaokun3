"""Verify all 264 trial008 logs before restoring only the isolated lab preparation mount."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('restore-baremetal-lab-workspace-rw-008.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-007-collected','baremetal-native-trial-008-collected'),
                ('baremetal-lab-workspace-rw-008.json','baremetal-lab-workspace-rw-009.json'),
                ('assert len(files) == 226','assert len(files) == 264')]:
    assert source.count(old)==1
    source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,'restore-lab-rw009','exec'))

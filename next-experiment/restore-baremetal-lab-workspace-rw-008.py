"""Verify all 226 preserved trial007 logs before restoring only isolated lab preparation flags."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('restore-baremetal-lab-workspace-rw-007.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-006-collected','baremetal-native-trial-007-collected'),
                ('baremetal-lab-workspace-rw-007.json','baremetal-lab-workspace-rw-008.json'),
                ('assert len(files) == 188','assert len(files) == 226')]:
    assert source.count(old)==1
    source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,'restore-lab-rw-008','exec'))

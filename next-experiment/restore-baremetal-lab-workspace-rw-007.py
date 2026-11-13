"""Verify all 188 saved trial006 raw logs before restoring isolated lab preparation flags."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('restore-baremetal-lab-workspace-rw-006.py')),run_name='offline_generator')['source']
for old,new in [('baremetal-native-trial-005-collected','baremetal-native-trial-006-collected'),('baremetal-lab-workspace-rw-006.json','baremetal-lab-workspace-rw-007.json'),('assert len(files) == 152','assert len(files) == 188')]:
    assert source.count(old)==1;source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,'restore-lab-rw-007','exec'))

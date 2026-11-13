"""Verify all 116 saved trial004 logs before restoring only lab preparation flags."""
from pathlib import Path

source=Path(__file__).with_name('restore-baremetal-lab-workspace-rw-002.py').read_text()
for old,new in [('baremetal-native-trial-001-evidence-immediate','baremetal-native-trial-004-collected'),('baremetal-lab-workspace-rw-002.json','baremetal-lab-workspace-rw-005.json'),('assert len(files) == 20','assert len(files) == 116')]:
    assert source.count(old)==1;source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,'restore-lab-rw-005','exec'))

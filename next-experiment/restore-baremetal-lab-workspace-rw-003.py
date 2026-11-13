"""Reconstructed adapter for historical trial002; DO NOT rerun completed operation.

The original adapter was accidentally overwritten while preparing trial012.
Original bytes were unavailable; behavior reconstructed from adapter004 and the
preserved report003 (50 logs). Existing report guards prevent execution.
"""
from pathlib import Path
source=Path(__file__).with_name('restore-baremetal-lab-workspace-rw-002.py').read_text()
for old,new in (
 ('baremetal-native-trial-001-evidence-immediate','baremetal-native-trial-002-collected'),
 ('baremetal-lab-workspace-rw-002.json','baremetal-lab-workspace-rw-003.json'),
 ('assert len(files) == 20','assert len(files) == 50'),
):
 assert source.count(old)==1
 source=source.replace(old,new)
exec(compile(source,'restore-lab-rw-003-reconstructed','exec'))

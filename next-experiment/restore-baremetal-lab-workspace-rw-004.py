"""Restore lab preparation flags after verifying all 82 collected trial003 logs."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'restore-baremetal-lab-workspace-rw-002.py').read_text()
for old, new in (
    ('baremetal-native-trial-001-evidence-immediate', 'baremetal-native-trial-003-collected'),
    ('baremetal-lab-workspace-rw-002.json', 'baremetal-lab-workspace-rw-004.json'),
    ('assert len(files) == 20', 'assert len(files) == 82'),
):
    assert source.count(old) == 1
    source = source.replace(old, new)
exec(compile(source, 'restore-lab-rw-004', 'exec'))

"""Archive/remove only consumed011 after independently verified trial008 return."""
from pathlib import Path
import json
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-004.py')))['launcher_source']()
    for old,new in [('boot-entry-cleanup-004','boot-entry-cleanup-005'),
                    ('baremetal-native-trial-007-collected','baremetal-native-trial-008-collected'),
                    ("len(collection['files']) == 226","len(collection['files']) == 264"),
                    ("(('007', '010'),)","(('008', '011'),)"),
                    ("for v in ('010',)","for v in ('011',)")]:
        assert old in source,old
        source=source.replace(old,new)
    return source

if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    verified=json.loads((base/'reports/baremetal-native-trial-008-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==264 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

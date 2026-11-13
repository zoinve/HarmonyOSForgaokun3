"""Archive/remove only consumed010 after independently verified native GPU trial007."""
from pathlib import Path
import json
import runpy


def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-003.py')))['launcher_source']()
    for old,new in [('boot-entry-cleanup-003','boot-entry-cleanup-004'),
                    ('baremetal-native-trial-006-collected','baremetal-native-trial-007-collected'),
                    ("len(collection['files']) == 188","len(collection['files']) == 226"),
                    ("(('006', '009'),)","(('007', '010'),)"),
                    ("for v in ('009',)","for v in ('010',)")]:
        assert old in source,old
        source=source.replace(old,new)
    return source


if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    verified=json.loads((base/'reports/baremetal-native-trial-007-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==226 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

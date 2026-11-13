"""Archive and remove only consumed014 after independently verified trial011 return."""
from pathlib import Path
import json
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-007.py')))['launcher_source']()
    for old,new in [('boot-entry-cleanup-007','boot-entry-cleanup-008'),
                    ('baremetal-native-trial-010','baremetal-native-trial-011'),
                    ("(('010', '013'),)","(('011', '014'),)"),
                    ('== 302','== 340')]:
        assert old in source,old
        source=source.replace(old,new)
    return source

if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    verified=json.loads((base/'reports/baremetal-native-trial-011-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==340 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

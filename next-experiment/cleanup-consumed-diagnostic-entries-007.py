"""Fresh cleanup record; retain the local006 backup made during preflight."""
from pathlib import Path
import json
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-006.py')))['launcher_source']()
    assert 'boot-entry-cleanup-006' in source
    return source.replace('boot-entry-cleanup-006','boot-entry-cleanup-007')

if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    verified=json.loads((base/'reports/baremetal-native-trial-010-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==302 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

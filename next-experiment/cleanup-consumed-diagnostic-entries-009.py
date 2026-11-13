"""Fresh record after008 stopped at its pre-removal candidate-set assertion."""
from pathlib import Path
import json
import runpy

def launcher_source():
    source=runpy.run_path(str(Path(__file__).with_name('cleanup-consumed-diagnostic-entries-008.py')))['launcher_source']()
    assert "for v in ('013',)" in source
    return source.replace('boot-entry-cleanup-008','boot-entry-cleanup-009').replace("for v in ('013',)","for v in ('014',)")

if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    verified=json.loads((base/'reports/baremetal-native-trial-011-independent-verification.json').read_text())
    assert verified['raw_log_sizes_and_hashes_verified']==340 and verified['one_shot_absent']
    exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})

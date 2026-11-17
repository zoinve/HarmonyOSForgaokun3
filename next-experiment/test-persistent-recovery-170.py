"""Keep trial 169 intact and test full recovery on a second local copy only."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    previous = json.loads((ROOT / 'reports/persistent-recovery-169/result.json').read_text())
    assert previous['copy_preen_exit'] == 4
    assert previous['copy_post_repair_fsck_exit'] == 4
    assert previous['backup_archive_unchanged'] and not previous['source_modified']
    source = (BASE / 'test-persistent-recovery-169.py').read_text()
    assert source.count("repair = check(copy, '-p', 'copy-only-preen')") == 1
    source = source.replace("REPORT = ROOT / 'reports/persistent-recovery-169'",
        "REPORT = ROOT / 'reports/persistent-recovery-170'")
    source = source.replace("WORK = ROOT / 'artifacts/persistent-recovery-169'",
        "WORK = ROOT / 'artifacts/persistent-recovery-170'")
    source = source.replace("repair = check(copy, '-p', 'copy-only-preen')",
        "repair = check(copy, '-y', 'copy-only-full-recovery')")
    source = source.replace('copy_preen_exit=repair', 'copy_manual_repair_exit=repair')
    exec(compile(source, 'test-persistent-recovery-170.generated.py', 'exec'),
        {'__name__': '__main__', '__file__': str(BASE / 'test-persistent-recovery-170.generated.py')})

"""Repeat read-only242 with deterministic diagnostic locale and expanded counts."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settings-storage-inspection-244.json'

if __name__ == '__main__':
    assert not REPORT.exists()
    remote = runpy.run_path(str(ROOT / 'next-experiment/inspect-settings-storage-242.py'))['REMOTE']
    remote = remote.replace("device='/dev/nvme0n1p4'", "os.environ['LC_ALL']='C'\ndevice='/dev/nvme0n1p4'", 1)
    remote = remote.replace('/mnt/settings-inspection-242', '/mnt/settings-inspection-244')
    old = "patterns={'journal_recovery_skipped':"
    assert remote.count(old) == 1
    remote = remote.replace(old, "patterns={'extent_exceeds_allowed':r'end of extent exceeds allowed value', 'inode_block_count_wrong':r'i_blocks is .*should be', 'dangling_directory_entry':r'deleted/unused inode', 'orphan_feature_without_entries':r'orphan_present is set but orphan file is clean', 'journal_recovery_skipped':", 1)
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['sudo -n python3 -'], input=remote, text=True,
                          capture_output=True, timeout=900)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    result.update(diagnostic_locale='C', supersedes_locale_sensitive_counts_242=True)
    REPORT.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

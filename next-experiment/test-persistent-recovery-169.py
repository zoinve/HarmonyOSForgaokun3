"""Try automatic ext4 recovery only on a hash-verified, disposable local copy."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/persistent-recovery-169'
WORK = ROOT / 'artifacts/persistent-recovery-169'

def check(path, mode, name):
    env = dict(os.environ, LC_ALL='C')
    proc = subprocess.run(['e2fsck', '-f', mode, str(path)],
        capture_output=True, text=True, timeout=180, env=env)
    (REPORT / (name + '.stdout')).open('x').write(proc.stdout)
    (REPORT / (name + '.stderr')).open('x').write(proc.stderr)
    return proc.returncode

if __name__ == '__main__':
    assert not REPORT.exists() and not WORK.exists(), 'preserve numbered recovery trial'
    metadata = json.loads((ROOT / 'reports/persistent-data-backup-169/result.json').read_text())
    assert metadata['decompressed_hash_verified'] and metadata['lab_partition_unmounted']
    archive = ROOT / metadata['backup_path']
    assert archive.resolve().is_relative_to((ROOT / 'artifacts/persistent-data-backup-169').resolve())
    assert not archive.is_symlink() and shutil.disk_usage(ROOT).free > 10 * 1024**3
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == metadata['compressed_sha256']
    REPORT.mkdir()
    WORK.mkdir(mode=0o700)
    copy = WORK / 'recovery-copy.ext4'
    digest = hashlib.sha256()
    with gzip.open(archive, 'rb') as source, copy.open('xb') as output:
        os.chmod(copy, 0o600)
        while chunk := source.read(4 * 1024 * 1024):
            output.write(chunk)
            digest.update(chunk)
        output.flush()
        os.fsync(output.fileno())
    assert digest.hexdigest() == metadata['source_sha256'] and copy.stat().st_size == metadata['source_bytes']
    assert copy.resolve().parent == WORK.resolve() and not copy.is_symlink()
    before = check(copy, '-n', 'before-readonly')
    print('Local copy verified; initial read-only fsck exit=' + str(before), flush=True)
    assert before == 4, 'unexpected baseline; do not repair'
    repair = check(copy, '-p', 'copy-only-preen')
    after = check(copy, '-n', 'after-readonly')
    with copy.open('rb') as stream:
        recovered_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == metadata['compressed_sha256']
    result = dict(source_modified=False,backup_archive_unchanged=True,
        repair_target=str(copy.relative_to(ROOT)),initial_fsck_exit=before,
        copy_preen_exit=repair,copy_post_repair_fsck_exit=after,
        recovered_sha256=recovered_sha,copy_recovered_cleanly=repair in [0,1] and after==0,
        original_disk_repaired=False,native_boot_performed=False)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

"""Compact verified local-only data artifacts without exporting private state."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
OUTPUT = ROOT / 'reports/private-settings-archive-230.json'
JOBS = {
    'settings-data-candidate-191-r2/data.ext4': 'f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce',
    'settingsdata-scaffolding-216/data.ext4': '0f14deabd956196c7f9b1543f6060e708c271eccfc8b4e4046807d75214891f4',
}

if __name__ == '__main__':
    assert os.geteuid() == 0 and not OUTPUT.exists()
    rows = []
    for relative, expected in JOBS.items():
        path = BUILD / relative
        assert path.resolve().is_relative_to(BUILD) and not path.is_symlink() and not path.parent.is_symlink()
        assert path.stat().st_size == 8589934592
        assert not subprocess.check_output(['losetup', '-j', str(path)]).strip()
        archive = path.with_name(path.name + '.gz')
        assert not archive.exists()
        before = path.stat()
        digest = hashlib.sha256()
        with path.open('rb') as source, archive.open('xb') as dest:
            os.fchmod(dest.fileno(), 0o600)
            with gzip.GzipFile(filename='', fileobj=dest, mode='wb', compresslevel=1, mtime=0) as compressor:
                while chunk := source.read(1024**2):
                    digest.update(chunk)
                    compressor.write(chunk)
            dest.flush()
            os.fsync(dest.fileno())
        assert digest.hexdigest() == expected
        with gzip.open(archive, 'rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected
        after = path.stat()
        assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
        path.unlink()
        rows.append(dict(original=str(path), archive=str(archive), original_sha256=expected,
            original_allocated_bytes=before.st_blocks * 512, archive_bytes=archive.stat().st_size,
            archive_allocated_bytes=archive.stat().st_blocks * 512, decompressed_hash_verified=True,
            private_local_archive=True, expanded_copy_deleted=True))
        print(json.dumps(dict(archived=relative, compressed_bytes=archive.stat().st_size)), flush=True)
    os.sync()
    result = dict(images=rows, reports_contain_no_raw_app_state=True, target_modified=False,
        allocated_bytes_saved=sum(row['original_allocated_bytes'] - row['archive_allocated_bytes'] for row in rows),
        restore_note='Restore the chosen private archive to a new guarded workspace before using a raw-image consumer.')
    OUTPUT.open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps(dict(archived_images=len(rows), allocated_bytes_saved=result['allocated_bytes_saved']), indent=2))

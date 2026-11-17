"""Finish obsolete report package cleanup and compress bulky auxiliary logs."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUTPUT = REPORTS / 'report-scratch-cleanup-228.json'
KEEP = {'commercial61-native-173', 'commercial61-native-206', 'commercial61-native-181'}


def safe(path):
    assert path.resolve().is_relative_to(REPORTS.resolve()) and not path.is_symlink()
    assert all(not parent.is_symlink() for parent in path.parents if parent.is_relative_to(REPORTS))
    assert path.is_file()


def sha(path, compressed=False):
    with (gzip.open(path, 'rb') if compressed else path.open('rb')) as stream:
        return hashlib.file_digest(stream, 'sha256').digest()


if __name__ == '__main__':
    assert not OUTPUT.exists()
    assert (REPORTS / 'historical-log-compression-226.json').is_file()
    names = [
        'composer-fd-package-001/initramfs.cpio.gz',
        'composer-parser-package-001/initramfs.cpio.gz',
        'composer-queue-package-001/initramfs.cpio.gz',
        'composer-fdstream-package-001/initramfs.cpio.gz',
        'commercial-software-codec-bundle-072/software-codec-runtime-072.tar.gz',
        'evidence-cleanup-220/verified-local-copies.json.gz',
    ]
    deleted = []
    for name in names:
        path = REPORTS / name
        if not path.exists():
            continue
        safe(path)
        size = path.stat().st_size
        path.unlink()
        deleted.append(dict(path=name, bytes=size))
    compressed = 0
    saved = 0
    for path in sorted(REPORTS.rglob('*')):
        if not path.is_file() or path.is_symlink() or path.stat().st_size < 65536:
            continue
        relative = path.relative_to(REPORTS)
        if relative.parts[0] in KEEP:
            continue
        if not (path.suffix in ['.log', '.stdout', '.stderr'] or
                path.name.endswith(('.stdout.txt', '.stderr.txt', '.disassembly.txt'))):
            continue
        safe(path)
        target = path.with_name(path.name + '.gz')
        assert not target.exists()
        before = path.stat()
        digest = sha(path)
        with path.open('rb') as source, target.open('xb') as dest:
            with gzip.GzipFile(filename='', mode='wb', fileobj=dest, compresslevel=6, mtime=0) as compressor:
                shutil.copyfileobj(source, compressor, 1024**2)
            dest.flush()
            os.fsync(dest.fileno())
        assert sha(target, compressed=True) == digest
        current = path.stat()
        assert (before.st_ino, before.st_size, before.st_mtime_ns) == (current.st_ino, current.st_size, current.st_mtime_ns)
        path.unlink()
        compressed += 1
        saved += before.st_size - target.stat().st_size
    result = dict(obsolete_package_or_temporary_table_files_deleted=deleted,
        auxiliary_logs_compressed=compressed, auxiliary_log_saved_bytes=saved,
        decompressed_hashes_verified=True, no_live_boot_payload_deleted=True,
        current173_206_and_usb181_preserved=True)
    OUTPUT.open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps(result, indent=2))

"""Losslessly compress completed historical raw logs; retain current diagnostics."""
from pathlib import Path, PureWindowsPath
import gzip
import hashlib
import io
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'reports/historical-log-compression-226.json'
KEEP = {'commercial61-native-173', 'commercial61-native-206', 'commercial61-native-181'}


def open_log(path):
    """Read canonical, compressed, or cumulative-prefix historical evidence."""
    path = Path(path)
    if path.is_file():
        return path.open('rb')
    compressed = path.with_name(path.name + '.gz')
    if compressed.is_file():
        return gzip.open(compressed, 'rb')
    prior = json.loads((ROOT / 'reports/evidence-cleanup-220/local.json').read_text())
    directory = path.parent.relative_to(ROOT).as_posix()
    rows = [row for row in prior['cumulative_log_redirects']
            if PureWindowsPath(row['directory']).as_posix() == directory and path.name in row['removed']]
    if len(rows) != 1:
        raise FileNotFoundError(path)
    metadata = json.loads((path.parent.parent / 'retrieval-manifest.json').read_text())['files'][path.name]
    with open_log(path.with_name(rows[0]['retained'])) as stream:
        data = stream.read(metadata['bytes'])
    assert hashlib.sha256(data).hexdigest() == metadata['sha256']
    return io.BytesIO(data)


if __name__ == '__main__':
    assert not OUTPUT.exists()
    result = dict(compressed_files=0, original_bytes=0, compressed_bytes=0, directories=[])
    for raw in sorted((ROOT / 'reports').glob('*/runtime-evidence/raw')):
        if raw.parent.parent.name in KEEP:
            continue
        assert raw.resolve().is_relative_to((ROOT / 'reports').resolve())
        assert not raw.is_symlink() and not raw.parent.is_symlink()
        count = 0
        for path in sorted(raw.glob('*.log')):
            assert path.is_file() and not path.is_symlink() and path.resolve().parent == raw.resolve()
            target = path.with_name(path.name + '.gz')
            assert not target.exists()
            before = path.stat()
            digest = hashlib.sha256()
            with path.open('rb') as source, target.open('xb') as dest:
                with gzip.GzipFile(filename='', mode='wb', fileobj=dest, compresslevel=6, mtime=0) as compressor:
                    while chunk := source.read(1024**2):
                        digest.update(chunk)
                        compressor.write(chunk)
                dest.flush()
                os.fsync(dest.fileno())
            with gzip.open(target, 'rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').digest() == digest.digest()
            current = path.stat()
            assert (before.st_ino, before.st_size, before.st_mtime_ns) == (current.st_ino, current.st_size, current.st_mtime_ns)
            path.unlink()
            result['compressed_files'] += 1
            result['original_bytes'] += before.st_size
            result['compressed_bytes'] += target.stat().st_size
            count += 1
        if count:
            result['directories'].append(dict(path=str(raw.relative_to(ROOT)), files=count))
            print(json.dumps(dict(compressed=raw.parent.parent.name, files=count)), flush=True)
    result['saved_bytes'] = result['original_bytes'] - result['compressed_bytes']
    result['all_decompressed_hashes_verified'] = True
    result['current173_206_and_usb181_logs_kept_plaintext'] = True
    result['reader'] = 'next-experiment/compress-historical-logs-226.py:open_log'
    OUTPUT.open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps({key: value for key, value in result.items() if key != 'directories'}, indent=2))

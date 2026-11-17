"""Retain canonical JSON and eliminate duplicate hash-table allocations."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
OUTPUT = REPORTS / 'duplicate-metadata-cleanup-223.json'


def safe(path):
    assert path.resolve().is_relative_to(REPORTS.resolve()) and not path.is_symlink()
    assert all(not parent.is_symlink() for parent in path.parents if parent.is_relative_to(REPORTS))
    assert path.is_file()


if __name__ == '__main__':
    assert not OUTPUT.exists()
    tables = []
    stdout_files = []
    for path in REPORTS.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        if 'hash' in path.name.lower() or 'manifest' in path.name.lower():
            tables.append(path)
        if path.suffix == '.stdout' or path.name == 'stdout':
            stdout_files.append(path)
    canonical = {}
    linked = []
    for path in sorted(tables):
        safe(path)
        data = path.read_bytes()
        info = path.stat()
        key = (len(data), hashlib.sha256(data).hexdigest(), info.st_mode,
               getattr(info, 'st_file_attributes', None))
        prior = canonical.get(key)
        if prior is None:
            canonical[key] = path
            continue
        if os.path.samefile(path, prior):
            continue
        temporary = path.with_name(path.name + '.dedup223')
        assert not temporary.exists()
        os.link(prior, temporary)
        assert temporary.read_bytes() == data
        os.replace(temporary, path)
        linked.append(dict(alias=str(path.relative_to(ROOT)),
                           canonical=str(prior.relative_to(ROOT)), bytes=len(data)))
    removed = []
    for path in stdout_files:
        if path.stat().st_size > 2 * 1024**2:
            continue
        safe(path)
        try:
            value = json.loads(path.read_bytes())
        except (ValueError, UnicodeError):
            continue
        for name in ['result.json', 'provision.json', 'transfer.json', 'source.json', 'target.json']:
            prior = path.parent / name
            if not prior.is_file() or prior.is_symlink():
                continue
            try:
                same = json.loads(prior.read_bytes()) == value
            except (ValueError, UnicodeError):
                continue
            if same:
                size = path.stat().st_size
                path.unlink()
                removed.append(dict(path=str(path.relative_to(ROOT)),
                    canonical=str(prior.relative_to(ROOT)), bytes=size))
                break
    result = dict(hash_table_files_inspected=len(tables),
        hash_table_logical_bytes=sum(path.stat().st_size for path in tables),
        duplicate_hash_tables_coalesced=linked, redundant_json_stdout_removed=removed,
        no_unique_hash_table_deleted=True, canonical_results_preserved=True)
    OUTPUT.open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps(dict(hash_table_files_inspected=len(tables),
        duplicate_hash_tables_coalesced=len(linked),
        duplicate_hash_table_bytes=sum(row['bytes'] for row in linked),
        redundant_json_stdout_removed=len(removed),
        redundant_stdout_bytes=sum(row['bytes'] for row in removed)), indent=2))

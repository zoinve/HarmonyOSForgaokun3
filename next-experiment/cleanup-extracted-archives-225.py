"""Delete extraction containers only after verifying all surviving/reconstructible members."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'reports/extracted-archive-cleanup-225.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


if __name__ == '__main__':
    assert not OUTPUT.exists()
    prior = json.loads((ROOT / 'reports/evidence-cleanup-220/local.json').read_text())
    redirects = {row['directory']: row for row in prior['cumulative_log_redirects']}
    removed = []
    kept = []
    for archive in sorted((ROOT / 'reports').glob('*/runtime-evidence/original.tar')):
        assert archive.resolve().is_relative_to((ROOT / 'reports').resolve())
        assert not archive.is_symlink() and not archive.parent.is_symlink()
        manifest = archive.parent / 'retrieval-manifest.json'
        if not manifest.is_file():
            kept.append(str(archive.relative_to(ROOT)))
            continue
        files = json.loads(manifest.read_text()).get('files')
        if not isinstance(files, dict):
            kept.append(str(archive.relative_to(ROOT)))
            continue
        raw = archive.parent / 'raw'
        redirect = redirects.get(str(raw.relative_to(ROOT)))
        final = raw / redirect['retained'] if redirect else None
        final_data = final.read_bytes() if final else None
        if final:
            assert hashlib.sha256(final_data).hexdigest() == files[final.name]['sha256']
        covered = set()
        valid = True
        with tarfile.open(archive, 'r:') as stream:
            for entry in stream:
                if entry.isdir() and entry.name in ['.', './']:
                    continue
                name = entry.name.removeprefix('./')
                if not entry.isfile() or len(PurePosixPath(name).parts) != 1 or name in covered:
                    valid = False
                    break
                metadata = files.get(name)
                if not isinstance(metadata, dict) or entry.size != metadata.get('bytes'):
                    valid = False
                    break
                path = raw / name
                if path.is_file() and not path.is_symlink():
                    digest = sha(path)
                elif final_data is not None and name in redirect['removed']:
                    assert len(final_data) >= entry.size
                    digest = hashlib.sha256(memoryview(final_data)[:entry.size]).hexdigest()
                else:
                    valid = False
                    break
                if digest != metadata['sha256']:
                    valid = False
                    break
                covered.add(name)
        if valid and covered == set(files):
            size = archive.stat().st_size
            archive.unlink()
            removed.append(dict(path=str(archive.relative_to(ROOT)), bytes=size,
                canonical_manifest=str(manifest.relative_to(ROOT)), verified_members=len(covered)))
            print(json.dumps(dict(removed=archive.parent.parent.name, bytes=size)), flush=True)
        else:
            kept.append(str(archive.relative_to(ROOT)))
    result = dict(removed_archives=removed, removed_bytes=sum(row['bytes'] for row in removed),
        archives_with_unverified_or_unique_members_retained=kept,
        extracted_logs_or_verified_final_prefixes_preserved=True,
        canonical_manifests_preserved=True)
    OUTPUT.open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps(dict(removed_archives=len(removed), removed_bytes=result['removed_bytes'],
        unverified_archives_retained=len(kept)), indent=2))

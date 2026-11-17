"""Deterministic, hash-pinned original tools for RAM extraction, not the ESP."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
STAGE = Path('/home/zoinve/harmony-virgl-883/native-wpa-083')
PACKAGE = STAGE.with_name('native-wpa-package-083')


def main():
    record = json.loads((STAGE / 'result.json').read_text())
    PACKAGE.mkdir(exist_ok=False)
    files = {}
    for row in record['files']:
        path = Path(row['path'])
        assert path.is_absolute() and '..' not in path.parts
        name = 'network083/' + str(path).lstrip('/')
        blob = (STAGE / str(path).lstrip('/')).read_bytes()
        assert len(blob) == row['bytes']
        assert hashlib.sha256(blob).hexdigest() == row['sha256']
        assert name not in files
        files[name] = blob
    assert sum(map(len, files.values())) < 32 * 1024 * 1024
    directories = {str(parent) for name in files for parent in Path(name).parents
                   if str(parent) not in ('.', 'network083')}
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for name in sorted(directories):
            info = tarfile.TarInfo(name)
            info.type, info.mode = tarfile.DIRTYPE, 0o755
            archive.addfile(info)
        for name, blob in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.mode, info.size = 0o755, len(blob)
            archive.addfile(info, io.BytesIO(blob))
    blob = gzip.compress(raw.getvalue(), compresslevel=9, mtime=0)
    assert len(blob) < 12 * 1024 * 1024
    with (PACKAGE / 'tools.tar.gz').open('xb') as stream:
        stream.write(blob)
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as archive:
        assert {m.name for m in archive if m.isfile()} == set(files)
        assert all(m.isdir() or m.isfile() for m in archive.getmembers())
        for name, expected in files.items():
            assert archive.extractfile(name).read() == expected
    result = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                  files=record['files'], package=str(PACKAGE / 'tools.tar.gz'),
                  destination='/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-wpa-tools-083/tools.tar.gz',
                  compressed_members=sorted(directories | set(files)),
                  credentials_read=False, esp_payload=False, runtime_verified=False)
    for output in (PACKAGE / 'result.json', ROOT / 'reports/commercial-network-inputs-audit-083/package.json'):
        with output.open('x') as stream:
            json.dump(result, stream, indent=2)
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()

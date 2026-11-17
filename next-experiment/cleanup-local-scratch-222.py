"""Delete failed private candidates and coalesce identical immutable binaries."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
REPORT = ROOT / 'reports/local-scratch-cleanup-222'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def metadata(path):
    info = path.stat()
    return (info.st_size, stat.S_IMODE(info.st_mode), info.st_uid, info.st_gid,
        tuple((name, os.getxattr(path, name)) for name in sorted(os.listxattr(path))))


if __name__ == '__main__':
    assert os.geteuid() == 0 and BUILD.resolve() == BUILD and not REPORT.exists()
    REPORT.mkdir()
    names = ['settings-data-candidate-191/data.ext4',
             'settings-data-candidate-191-r1/data.ext4',
             'settingsdata-scaffolding-215/data.ext4']
    paths = [BUILD / name for name in names]
    for path in paths:
        assert path.resolve().is_relative_to(BUILD) and not path.is_symlink() and not path.parent.is_symlink()
        assert not subprocess.check_output(['losetup', '-j', str(path)]).strip()
    open_inodes = set()
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            for fd in (process / 'fd').iterdir():
                try:
                    info = fd.stat()
                    open_inodes.add((info.st_dev, info.st_ino))
                except (FileNotFoundError, ProcessLookupError):
                    pass
        except (FileNotFoundError, ProcessLookupError):
            pass
    removed = []
    for path in paths:
        if not path.exists():
            continue
        info = path.stat()
        assert stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) not in open_inodes
        path.unlink()
        removed.append(dict(path=str(path.relative_to(BUILD)), allocated_bytes=info.st_blocks * 512))
    canonical = {}
    coalesced = 0
    saved = 0
    for directory in sorted(BUILD.glob('commercial61-native-*')):
        if not re.fullmatch(r'commercial61-native-[0-9]{3}', directory.name):
            continue
        assert directory.resolve().parent == BUILD and not directory.is_symlink()
        for name in ['bootstrap-runtime087', 'init']:
            path = directory / name
            if not path.is_file() or path.is_symlink():
                continue
            info = path.stat()
            if (info.st_dev, info.st_ino) in open_inodes:
                continue
            key = (metadata(path), sha(path))
            source = canonical.get(key)
            if source is None:
                canonical[key] = path
                continue
            if source.stat().st_ino == info.st_ino or info.st_nlink != 1:
                continue
            temporary = path.with_name(path.name + '.dedup222')
            assert not temporary.exists()
            os.link(source, temporary)
            assert metadata(temporary) == key[0] and sha(temporary) == key[1]
            os.replace(temporary, path)
            coalesced += 1
            saved += info.st_blocks * 512
    os.sync()
    result = dict(deleted_failed_candidates=removed, identical_binaries_coalesced=coalesced,
        deduplicated_allocated_bytes=saved, all_binary_paths_and_bytes_preserved=True,
        original_images_modified=False, source191r2_or_candidate216_modified=False,
        target_machine_modified=False)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

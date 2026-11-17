"""Read-only ZIP structure audit; not a signature verifier or boot experiment."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/commercial-bundle-inputs-audit-066'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
PATHS = (
    '/system/app/Settings/Settings.hap',
    '/system/app/PCSettings/PCSettings.hap',
    '/system/app/Camera/Camera.hap',
    '/system/app/AppGallery/@hw-ae-business+app-assist-4-developer.hsp',
    '/system/app/SceneBoard/SceneBoard_EngineService.hap',
)


def inspect(path):
    blob = path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        ends = []
        invalid_headers = []
        for member in archive.infolist():
            header = struct.unpack_from('<4s5H3I2H', blob, member.header_offset)
            if header[0] != b'PK\x03\x04':
                invalid_headers.append(dict(name=member.filename, offset=member.header_offset))
                continue
            ends.append(member.header_offset + 30 + header[-2] + header[-1]
                        + member.compress_size)
        end = max(ends) if ends and not invalid_headers else None
        gap = blob[end:archive.start_dir] if end is not None else None
        metadata = {}
        for name in ('module.json', 'config.json', 'pack.info'):
            if name in archive.namelist():
                metadata[name] = json.loads(archive.read(name))
        return dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                    zip_crc_valid=bad is None, zip_crc_bad_member=bad,
                    entries=len(archive.infolist()), invalid_local_headers=invalid_headers,
                    central_directory_offset=archive.start_dir,
                    last_entry_payload_end=end,
                    pre_central_gap_bytes=len(gap) if gap is not None else None,
                    pre_central_tail_hex=gap[-64:].hex() if gap is not None else None,
                    metadata=metadata, cryptographic_signature_verified=False)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=False)
    rows = []
    for source in PATHS:
        target = OUT / Path(source).name
        result = subprocess.run(['debugfs', '-R', 'dump ' + source + ' ' + str(target),
                                 str(IMAGE)], capture_output=True, check=True)
        assert target.is_file() and target.stat().st_size > 0, result.stderr
        row = inspect(target)
        row['original_path'] = source
        rows.append(row)
    result = dict(original_image=str(IMAGE), original_image_modified=False,
                  operational_boot_performed=False, signature_checks_modified=False,
                  zip_gap_is_not_cryptographic_verification=True, files=rows)
    with (OUT / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=True)
    for row in rows:
        print(row['original_path'], 'bytes=', row['bytes'],
              'gap=', row['pre_central_gap_bytes'], 'sha256=', row['sha256'])

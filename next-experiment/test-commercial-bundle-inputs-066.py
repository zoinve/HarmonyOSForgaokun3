"""Check unsigned ZIP structure and retain corruption without hiding it."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location(
    'bundle066', Path(__file__).with_name('audit-commercial-bundle-inputs-066.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'fixture.hap'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('module.json', '{"app":{"bundleName":"test.fixture"}}')
        archive.writestr('ets/modules.abc', b'test-payload')
    row = audit.inspect(path)
    assert row['zip_crc_valid'] and row['pre_central_gap_bytes'] == 0
    assert not row['cryptographic_signature_verified']
    blob = bytearray(path.read_bytes())
    with zipfile.ZipFile(path) as archive:
        member = archive.getinfo('ets/modules.abc')
        offset = member.header_offset
        header = struct.unpack_from('<4s5H3I2H', blob, offset)
        payload = offset + 30 + header[-2] + header[-1]
    blob[payload] ^= 1
    path.write_bytes(blob)
    row = audit.inspect(path)
    assert not row['zip_crc_valid']
    assert row['zip_crc_bad_member'] == 'ets/modules.abc'
    assert row['pre_central_gap_bytes'] == 0
print('PASS: ZIP CRC failure retained; unsigned structure never called verified')

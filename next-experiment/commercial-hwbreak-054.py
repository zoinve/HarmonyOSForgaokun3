"""Observe the actual transaction consumer and original render boundaries."""
from pathlib import Path
import hashlib
import json
import struct

BASE = Path(__file__).resolve().parents[1]


def specifications():
    audit = json.loads((BASE / 'reports/commercial-render-audit-054/result.json').read_text())
    assert audit['original_elf_hashes_verified'] and audit['executable_offsets_verified']
    specs = audit['probes']
    assert [row['event'] for row in specs] == ['transaction_process', 'process_command', 'render', 'uni_render']
    for row in specs:
        filename = 'base.so' if row['library'] == 'librender_service_base.z.so' else 'service.so'
        data = (BASE / 'reports/commercial-oneway-audit-045' / filename).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row['sha256']
        assert data[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', data, 18)[0] == 183
        offset, address = int(row['file_offset'], 16), int(row['virtual_address'], 16)
        assert data[offset:offset+4] == bytes.fromhex(row['original_instruction'])
        start = struct.unpack_from('<Q', data, 32)[0]
        size, count = struct.unpack_from('<HH', data, 54)
        matched = False
        for index in range(count):
            kind, flags, file_offset, virtual, _, file_size, _, _ = struct.unpack_from('<IIQQQQQQ', data, start + index*size)
            if kind == 1 and flags & 1 and file_offset <= offset and offset + 4 <= file_offset + file_size:
                assert virtual + offset - file_offset == address
                matched = True
        assert matched and address % 4 == 0
    return specs


def instrument(source):
    prefix = 'static const struct hw050_spec hw050_specs[]={'
    start = source.index(prefix) + len(prefix)
    end = source.index('};', start)
    specs = ['{' + ','.join([json.dumps(row['event']), json.dumps(row['library']),
                             row['file_offset'] + 'ULL',
                             hex(int.from_bytes(bytes.fromhex(row['original_instruction']), 'little')) + 'u']) + '}'
             for row in specifications()]
    return source[:start] + ',\n'.join(specs) + source[end:]

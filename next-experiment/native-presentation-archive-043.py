"""Bounded-memory newc reader. No extraction, target execution or device access."""
import hashlib


def exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise EOFError(f'truncated newc record: need {size}, got {len(data)}')
    return data


def scan_cpio(stream, keep):
    records, selected = {}, {}
    while True:
        header = exact(stream, 110)
        assert header[:6] == b'070701', 'unexpected archive encoding'
        values = [int(header[6 + 8*i:14 + 8*i], 16) for i in range(13)]
        size, namesize = values[6], values[11]
        assert 1 <= namesize <= 4096 and size <= 8 * 1024**3
        name = exact(stream, namesize)
        assert name[-1:] == b'\0' and b'\0' not in name[:-1]
        name = name[:-1].decode('utf-8')
        assert not any(exact(stream, (-(110 + namesize)) % 4))
        if name == 'TRAILER!!!':
            assert size == 0
            tail = stream.read(65537)
            assert len(tail) <= 65536 and not any(tail), 'unexpected trailing archive'
            break
        assert name not in records and len(records) < 20000, 'duplicate or excessive archive records'
        capture = name in keep
        assert not capture or size <= 2 * 1024**2, 'selected member exceeds small-file limit'
        digest, pieces, left = hashlib.sha256(), [], size
        while left:
            part = exact(stream, min(left, 1024**2))
            digest.update(part)
            if capture:
                pieces.append(part)
            left -= len(part)
        assert not any(exact(stream, (-size) % 4))
        records[name] = dict(header=values, bytes=size, sha256=digest.hexdigest(),
                             metadata=values[:6] + values[7:])
        if capture:
            selected[name] = b''.join(pieces)
    assert set(keep) <= set(selected), 'missing selected archive member'
    return records, selected


def emit_member(name, record, data):
    assert len(data) == record['bytes']
    assert hashlib.sha256(data).hexdigest() == record['sha256']
    encoded = name.encode() + b'\0'
    fields = record['header']
    assert fields[6] == len(data) and fields[11] == len(encoded)
    header = b'070701' + ''.join(f'{v:08x}' for v in fields).encode()
    return header + encoded + b'\0' * ((-(110 + len(encoded))) % 4) + data + b'\0' * ((-len(data)) % 4)


def trailer():
    name = b'TRAILER!!!\0'
    fields = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(name), 0]
    return b'070701' + ''.join(f'{v:08x}' for v in fields).encode() + name + b'\0' * ((-(110 + len(name))) % 4)

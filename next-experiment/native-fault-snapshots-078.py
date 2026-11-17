"""Accept only exact, contiguous, complete original diagnostic snapshots."""
import re

BEGIN = re.compile(rb'NATIVE_FAULT018_BEGIN sample=(\d+) path=(\S+) size=(\d+) fd=(\d+) errno=0')
HEX = re.compile(rb'NATIVE_FAULT018_HEX sample=(\d+) path=(\S+) offset=(\d+) data=([0-9a-f]+)')
END = re.compile(rb'NATIVE_FAULT018_END sample=(\d+) path=(\S+) bytes=(\d+) complete=(\d+) changed=(\d+) read_errno=(\d+)')


def extract(body):
    active, accepted, rejected = {}, [], []
    for line in body.splitlines():
        match = BEGIN.fullmatch(line)
        if match:
            key = int(match[1]), match[2].decode('ascii')
            if key in active:
                rejected.append(dict(sample=key[0], path=key[1], reason='duplicate_begin'))
            size = int(match[3])
            active[key] = dict(sample=key[0], path=key[1], size=size, data=bytearray(),
                               valid=0 <= size <= 2097152, reason='size_limit')
            continue
        match = HEX.fullmatch(line)
        if match:
            key = int(match[1]), match[2].decode('ascii')
            row = active.get(key)
            if row is None or not row['valid']:
                continue
            if int(match[3]) != len(row['data']) or len(match[4]) % 2:
                row.update(valid=False, reason='noncontiguous_or_malformed_hex')
                continue
            chunk = bytes.fromhex(match[4].decode('ascii'))
            if not 0 < len(chunk) <= 128 or len(row['data']) + len(chunk) > row['size']:
                row.update(valid=False, reason='chunk_size_or_file_size')
                continue
            row['data'].extend(chunk)
            continue
        match = END.fullmatch(line)
        if match:
            key = int(match[1]), match[2].decode('ascii')
            row = active.pop(key, None)
            if row is None:
                continue
            complete = tuple(map(int, match.group(3, 4, 5, 6))) == (row['size'], 1, 0, 0)
            if row['valid'] and complete and len(row['data']) == row['size']:
                accepted.append(dict(sample=key[0], path=key[1], data=bytes(row['data'])))
            else:
                rejected.append(dict(sample=key[0], path=key[1],
                                     reason=row['reason'] if not row['valid'] else 'incomplete_changed_or_read_error'))
    rejected.extend(dict(sample=k[0], path=k[1], reason='missing_end') for k in active)
    return accepted, rejected

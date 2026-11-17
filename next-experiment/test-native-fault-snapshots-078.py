from pathlib import Path
import runpy

extract = runpy.run_path(str(Path(__file__).with_name('native-fault-snapshots-078.py')))['extract']


def snapshot(sample, content=b'abc', offset=0, complete=1, changed=0):
    return (f'NATIVE_FAULT018_BEGIN sample={sample} path=/x size=3 fd=7 errno=0\n'
            f'NATIVE_FAULT018_HEX sample={sample} path=/x offset={offset} data={content.hex()}\n'
            f'NATIVE_FAULT018_END sample={sample} path=/x bytes=3 complete={complete} changed={changed} read_errno=0\n').encode()


good = snapshot(0)
assert extract(good)[0] == [dict(sample=0, path='/x', data=b'abc')]
for bad in [snapshot(1, offset=1), snapshot(1, content=b'ab'), snapshot(1, changed=1),
            snapshot(1, complete=0), good.replace(b'data=616263', b'data=616Z263'),
            b'\n'.join(good.splitlines()[:-1])]:
    assert not extract(bad)[0]
    accepted, rejected = extract(bad + b'\n' + snapshot(2))
    assert accepted == [dict(sample=2, path='/x', data=b'abc')]
    assert rejected
interleaved = good.replace(b'data=616263', b'data=616noise263')
assert not extract(interleaved)[0]
assert extract(b'unrelated log\n' + good)[0]
print('PASS: intact, truncated, changed, missing, malformed and later-copy cases')

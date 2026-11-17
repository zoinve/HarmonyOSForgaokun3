from pathlib import Path
import runpy

p = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-presentation-066.py')))
begin = b'COMMERCIAL043_STREAM_BEGIN sample=3 pid=0 path=/data/native-perf-023.trace limit=262144\n'
end = b'\nCOMMERCIAL043_STREAM_END sample=3 pid=0 path=/data/native-perf-023.trace bytes=4 eof=1 errno=0'
assert p['streams'](begin + b'abc\n' + end)[0]['body'] == b'abc\n'
assert not p['streams'](begin + b'abc\n')
assert not p['streams']((begin + b'abc\n' + end).replace(b'native-perf-023.trace', b'other.trace'))
try:
    p['streams'](begin + b'abcd\n' + end)
except AssertionError:
    pass
else:
    raise AssertionError('Corrupt byte count was accepted')
line = b'COMMERCIAL030_FRAME ' + b' '.join(key.encode() + b'=1' for key in sorted(p['FIELDS']))
assert len(p['frames'](line)) == 1
assert not p['frames'](line.replace(b'gpu_owned=1', b'gpu_ow'))
print('PASS: complete/truncated streams, wrong path, byte corruption, incomplete frame rejected')

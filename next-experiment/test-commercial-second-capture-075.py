"""Compile and execute the exact second-export worker under ASan/UBSan."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

b = Path(__file__).resolve().parent
work = Path('/home/zoinve/harmony-virgl-883/commercial-second-capture-test-075')
report = b.parent / 'reports/commercial-second-capture-test-075'
work.mkdir()
report.mkdir()
native = runpy.run_path(str(b / 'build-commercial-native-075.py'))
start = native['outer'].index('static void full075_export_worker')
end = native['outer'].index('static void native_full_export075', start)
worker = native['outer'][start:end]
header = (b / 'native-full-export-068.h').read_text().split('static void full068_export_worker', 1)[0] + worker
(work / 'second-export.h').open('x').write(header)
source = (b / 'test-native-full-capture-068.cpp').read_text().replace(
    '#include "native-full-export-068.h"', '#include "second-export.h"').replace(
    'full068_export_worker(&context)', 'full075_export_worker(&context)').replace('120123456', '140123456')
(work / 'test.cpp').open('x').write(source)
command = ['g++', '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Werror',
           '-fsanitize=address,undefined', '-g', '-I', str(b), '-I', str(work), str(work / 'test.cpp'), '-o', str(work / 'test')]
compiled = subprocess.run(command, capture_output=True)
(report / 'compile.stdout').open('xb').write(compiled.stdout)
(report / 'compile.stderr').open('xb').write(compiled.stderr)
assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
tested = subprocess.run([str(work / 'test'), str(work)], capture_output=True, timeout=30)
(report / 'test.stdout').open('xb').write(tested.stdout)
(report / 'test.stderr').open('xb').write(tested.stderr)
assert tested.returncode == 0, tested.stderr.decode(errors='replace')
expected = b'P6\n3 2\n255\n' + bytes(v for y in range(2) for x in range(3) for v in [10+y*20+x, 30+x, 80+y])
for name in ['source', 'output']:
    assert (work / 'input' / (name + '.ppm')).read_bytes() == expected
    assert (work / 'output' / ('full-' + name + '-075.ppm')).read_bytes() == expected
assert (work / 'input/ready').read_bytes() == (work / 'output/full-ready-075').read_bytes()
assert not list((work / 'output').glob('*068*'))
for path in work.glob('reject-*'):
    assert not (path / 'full-ready-075').exists()
result = dict(exact_second_export_worker_sha256=hashlib.sha256(worker.encode()).hexdigest(),
    actual_worker_executed=True, asan_ubsan_clean=not tested.stderr,
    rgba_bgra_stride_pixels_exact=True, second_names_distinct=True,
    existing_outputs_preserved=True, partial_owner_symlink_size_failures_rejected=True,
    source_pixel_buffers_unchanged=True, desktop_verified=False, interaction_verified=False)
(report / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

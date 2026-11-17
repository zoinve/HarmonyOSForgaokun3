"""Compiled exact helpers, pixel-exact fixture and no-overwrite/export guards."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'commercial-full-capture-test-068'
work.mkdir()
command = ['g++', '-std=c++17', '-pthread', '-Wall', '-Wextra', '-Werror',
           '-fsanitize=address,undefined', '-g', '-I', str(b),
           str(b / 'test-native-full-capture-068.cpp'), '-o', str(work / 'test')]
compile_result = subprocess.run(command, capture_output=True)
(work / 'compile.stdout').open('xb').write(compile_result.stdout)
(work / 'compile.stderr').open('xb').write(compile_result.stderr)
assert compile_result.returncode == 0, compile_result.stderr.decode(errors='replace')
result = subprocess.run([str(work / 'test'), str(work)], capture_output=True)
(work / 'test.stdout').open('xb').write(result.stdout)
(work / 'test.stderr').open('xb').write(result.stderr)
assert result.returncode == 0, result.stderr.decode(errors='replace')
expected = b'P6\n3 2\n255\n' + bytes(v for y in range(2) for x in range(3)
                                   for v in [10+y*20+x, 30+x, 80+y])
for prefix in ['input/source.ppm', 'input/output.ppm',
               'output/full-source-068.ppm', 'output/full-output-068.ppm']:
    assert (work / prefix).read_bytes() == expected, prefix
assert (work / 'input/ready').read_bytes() == (work / 'output/full-ready-068').read_bytes()
assert not (work / 'not-created').exists()
for path in work.glob('reject-*'):
    assert not (path / 'full-ready-068').exists(), path

instrument = runpy.run_path(str(b / 'commercial-full-frame-068.py'))
before = (root / 'commercial-composer-030/composer-evidence-030.cpp').read_text()
after = (root / 'commercial-composer-068/composer-evidence-068.cpp').read_text()
assert after == instrument['instrument'](before)
assert after.replace(instrument['HELPER']+'\n', '', 1).replace(
    '    full068_capture(buffer);\n', '', 1) == before
gate = runpy.run_path(str(b / 'commercial-full-export-068.py'))
old = runpy.run_path(str(b / 'build-commercial-native-067.py'))
new = runpy.run_path(str(b / 'build-commercial-native-068.py'))
assert new['inner'] == gate['inner'](old['inner'])
assert new['outer'] == gate['outer'](old['outer']).replace(
    'commercial61-native-067', 'commercial61-native-068').replace('COMMERCIAL067', 'COMMERCIAL068')
manifest = dict(compiled_helpers_passed=True, address_undefined_sanitizers_passed=True,
                pixel_exact_rgba_bgra_and_stride=True, source_maps_unchanged=True,
                partial_publish_rejected=True, existing_outputs_never_overwritten=True,
                wrong_owner_symlink_oversize_and_malformed_rejected=True,
                exact_composer_source_addition=True, exact_bootstrap_export_additions=True,
                bounded_outer_export_ms=8000, full_capture_count_max=1,
                header_sha256={name: hashlib.sha256((b / name).read_bytes()).hexdigest()
                    for name in ['native-full-capture-068.h', 'native-full-export-068.h']},
                desktop_verified=False, target_runtime_verified=False)
out = b.parent / 'reports/commercial-full-capture-test-068.json'
with out.open('x') as f:
    json.dump(manifest, f, indent=2)
print(json.dumps(manifest, indent=2))

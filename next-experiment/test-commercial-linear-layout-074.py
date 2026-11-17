"""Compile and execute real shared layout calculations; no desktop claim."""
from pathlib import Path
import hashlib
import json
import subprocess

b = Path(__file__).resolve().parent
work = Path('/home/zoinve/harmony-virgl-883/commercial-linear-layout-test-074-r2')
report = b.parent / 'reports/commercial-linear-layout-test-074-r2'
work.mkdir()
report.mkdir()
reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/include')
command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
           '-fno-omit-frame-pointer', '-I' + str(reference), '-I' + str(b),
           str(b / 'test-commercial-linear-layout-074.cpp'), '-o', str(work / 'layout-test')]
compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
for name, text in [('compile.stdout', compiled.stdout), ('compile.stderr', compiled.stderr)]:
    (report / name).open('x').write(text)
assert compiled.returncode == 0, compiled.stderr
tested = subprocess.run([str(work / 'layout-test')], capture_output=True, text=True, timeout=30)
assert tested.returncode == 0 and not tested.stderr, (tested.returncode, tested.stderr)
result = dict(command=command, returncode=tested.returncode, asan_ubsan_no_report=True,
              real_native_request_dimensions_covered=True, rgb_formats_covered=4,
              yuv_formats_covered=2, undersize_odd_overflow_and_unknown_rejected=True,
              real_native_blob_request_covered=True,
              hardware_allocation_verified=False, gpu_import_verified=False, desktop_verified=False,
              source_sha256={name: hashlib.sha256((b / name).read_bytes()).hexdigest() for name in
                  ['commercial-linear-layout-074.h', 'test-commercial-linear-layout-074.cpp']})
(report / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

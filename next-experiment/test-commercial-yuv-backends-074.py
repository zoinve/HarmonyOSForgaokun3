"""Actual transformed VDI and image-attribute code with mocked DRM only."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
built = root / 'commercial-yuv-074-r3'
work = root / 'commercial-yuv-backend-test-074-r3'
report = b.parent / 'reports/commercial-yuv-backend-test-074-r3'
work.mkdir()
report.mkdir()
provenance = json.loads((built / 'result.json').read_text())
module = runpy.run_path(str(b / 'commercial-yuv-074.py'))
assert hashlib.sha256((built / 'commercial-linear-layout-074.h').read_bytes()).hexdigest() == provenance['header_sha256']
assert hashlib.sha256((built / 'allocator-074.cpp').read_bytes()).hexdigest() == provenance['artifacts']['allocator']['source_sha256']
assert module['IMAGE_HELPER'] in (built / 'egl-074.cpp').read_text()
(work / 'image-helper-074.h').open('x').write(module['IMAGE_HELPER'])
reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
    '-I' + str(reference), '-I' + str(reference / 'include'), '-I/usr/include/libdrm',
    '-I' + str(root / 'prefix/system/include'), '-I' + str(root / 'prefix/system/include/libdrm'),
    '-I' + str(built), '-I' + str(work),
    str(b / 'test-commercial-yuv-backends-074.cpp'), '-Wl,--wrap=ioctl', '-o', str(work / 'backend-test')]
compile_result = subprocess.run(command, capture_output=True, text=True, timeout=60)
for suffix, text in [('stdout', compile_result.stdout), ('stderr', compile_result.stderr)]:
    (report / ('compile.' + suffix)).open('x').write(text)
assert compile_result.returncode == 0, compile_result.stderr
run = subprocess.run([str(work / 'backend-test')], capture_output=True, text=True, timeout=30)
for suffix, text in [('stdout', run.stdout), ('stderr', run.stderr)]:
    (report / ('test.' + suffix)).open('x').write(text)
assert run.returncode == 0, (run.returncode, run.stderr[-6000:])
assert not any(token in run.stderr for token in ['AddressSanitizer', 'runtime error:', 'LeakSanitizer'])
result = dict(command=command, allocator_source_sha256=provenance['artifacts']['allocator']['source_sha256'],
    header_sha256=provenance['header_sha256'], image_helper_sha256=hashlib.sha256(module['IMAGE_HELPER'].encode()).hexdigest(),
    asan_ubsan_no_report=True, real_transformed_allocator_executed=True, drm_explicitly_mocked=True,
    native_hardware_allocation_verified=False, gpu_import_verified=False,
    rgb_yuv_blob_allocation_and_mapping_passed=True, layout_row_and_column_stride_verified=True,
    yuv_egl_two_plane_attributes_verified=True, blob_egl_import_rejected=True,
    short_backing_rejected=True, protected_rejected=True, expected_size_enforced=True,
    allocation_failure_cleanup_and_fd_count_verified=True, desktop_verified=False)
(report / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))

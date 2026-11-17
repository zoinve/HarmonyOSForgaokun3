"""Require exact tested code, read-only integration and complete incremental chain."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
report = b.parent / 'reports/commercial61-native-074'
module = runpy.run_path(str(b / 'commercial-yuv-074.py'))
build = json.loads((root / 'commercial-yuv-074-r3/result.json').read_text())
test = json.loads((b.parent / 'reports/commercial-yuv-backend-test-074-r3/result.json').read_text())
geometry = json.loads((b.parent / 'reports/commercial-linear-layout-test-074-r2/result.json').read_text())
assert test['allocator_source_sha256'] == build['artifacts']['allocator']['source_sha256']
assert test['header_sha256'] == build['header_sha256'] == geometry['source_sha256']['commercial-linear-layout-074.h']
assert test['image_helper_sha256'] == hashlib.sha256(module['IMAGE_HELPER'].encode()).hexdigest()
assert all(test[key] for key in ['asan_ubsan_no_report', 'real_transformed_allocator_executed',
    'rgb_yuv_blob_allocation_and_mapping_passed', 'layout_row_and_column_stride_verified',
    'yuv_egl_two_plane_attributes_verified', 'blob_egl_import_rejected', 'short_backing_rejected',
    'protected_rejected', 'expected_size_enforced', 'allocation_failure_cleanup_and_fd_count_verified'])
assert geometry['asan_ubsan_no_report'] and geometry['real_native_blob_request_covered']
for role, parent, source_name, binary_name in [
    ('allocator', 'commercial-allocator-073', 'buffer-vdi.cpp', 'libdisplay_buffer_vdi_impl.z.so'),
    ('egl', 'commercial-egl-067', 'egl-trace-067.cpp', 'libEGL_impl.so')]:
    source = module[role]((root / parent / source_name).read_text())
    assert hashlib.sha256(source.encode()).hexdigest() == build['artifacts'][role]['source_sha256']
    assert hashlib.sha256((root / 'commercial-yuv-074-r3' / binary_name).read_bytes()).hexdigest() == build['artifacts'][role]['binary_sha256']
before_source = runpy.run_path(str(b / 'build-commercial-native-073.py'))
after_source = runpy.run_path(str(b / 'build-commercial-native-074.py'))
expected = before_source['inner'].replace('"/allocator073/libdisplay_buffer_vdi_impl.z.so"',
                                         '"/allocator074/libdisplay_buffer_vdi_impl.z.so"')
expected = expected.replace('commercial_copy005("/graphics016/system/lib64/libEGL_impl.so",',
                            'commercial_copy005("/egl074/libEGL_impl.so",')
assert after_source['inner'] == expected
assert after_source['outer'] == before_source['outer'].replace('commercial61-native-073', 'commercial61-native-074').replace('COMMERCIAL073', 'COMMERCIAL074')
assert all(marker in expected for marker in ['mount("overlay","/system","overlay",MS_RDONLY,options)',
                                             'mount("overlay","/vendor","overlay",MS_RDONLY,options)'])
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))],
                      type_ignores=[]), 'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-073/initrd.img')
after = helpers['parse'](root / 'commercial61-native-074/initrd.img')
assert set(before) <= set(after)
changed = sorted(name for name in before if before[name] != after[name])
assert changed == ['init', 'native-target/bootstrap']
added = sorted(set(after) - set(before))
assert added == ['native-target/allocator074', 'native-target/allocator074/libdisplay_buffer_vdi_impl.z.so',
                 'native-target/egl074', 'native-target/egl074/libEGL_impl.so']
for folder, role, name in [('allocator074', 'allocator', 'libdisplay_buffer_vdi_impl.z.so'),
                           ('egl074', 'egl', 'libEGL_impl.so')]:
    assert hashlib.sha256(after['native-target/' + folder + '/' + name][1]).hexdigest() == build['artifacts'][role]['binary_sha256']
overlay = json.loads((report / 'overlay-result.json').read_text())
parent = json.loads((b.parent / 'reports/commercial61-native-073/overlay-result.json').read_text())
assert overlay['chain'] == parent['chain'] + ['commercial61-native-074/initrd.img']
assert overlay['shared_parent_overlay_sha256'] == parent['sha256'] and overlay['ordered_chain_equals_full_074']
assert build['original_commercial_runtime'] and build['egl_public_exports_unchanged']
result = dict(tested_exact_backend_sources=True, exact_archive_delta=True,
    original_service_identities_unchanged=True, original_codec_and_resources_unchanged=True,
    protected_buffers_still_rejected=True, readonly_overlays=True, shared_parent_chain_verified=True,
    egl_system_and_passthrough_updated=True, existing_members_changed=changed, added_members=added,
    backend_build='commercial-yuv-074-r3', backend_tests='commercial-yuv-backend-test-074-r3',
    unit_tests_use_mock_drm=True, native_allocation_verified=False, gpu_import_verified=False,
    desktop_verified=False, interaction_verified=False)
(report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
workflow = runpy.run_path(str(b / 'commercial-workflow-074.py'))
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return']:
    compile(workflow['source074'](name), name, 'exec')
print(json.dumps(result, indent=2))

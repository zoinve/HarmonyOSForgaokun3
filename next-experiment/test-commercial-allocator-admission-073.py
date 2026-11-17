"""Executed only after genuine builds/tests; no source-only success shortcut."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import stat

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
report = b.parent / 'reports/commercial61-native-073'
observer = runpy.run_path(str(b / 'commercial-allocator-observer-073.py'))
old = runpy.run_path(str(b / 'build-commercial-native-072.py'))
new = runpy.run_path(str(b / 'build-commercial-native-073.py'))
assert new['inner'] == observer['inner'](old['inner'])
assert new['outer'].replace('commercial61-native-073', 'commercial61-native-072').replace('COMMERCIAL073', 'COMMERCIAL072') == old['outer']
assert 'mount("overlay","/system","overlay",MS_RDONLY,options)' in new['inner']
assert 'mount("overlay","/vendor","overlay",MS_RDONLY,options)' in new['inner']
logger = json.loads((b.parent / 'reports/commercial-allocator-logger-test-073-r2/result.json').read_text())
assert logger['logger_sha256'] == hashlib.sha256(observer['LOGGER'].encode()).hexdigest()
assert all(logger[key] for key in ['bounded_to_128_requests', 'four_thread_logging_complete',
    'request_fields_preserved', 'errno_preserved', 'missing_trace_not_created',
    'symlink_target_unchanged', 'asan_ubsan_no_report'])
allocator = json.loads((root / 'commercial-allocator-073/result.json').read_text())
source = (root / 'commercial-allocator-073/buffer-vdi.cpp').read_bytes()
assert hashlib.sha256(source).hexdigest() == allocator['source_sha256']
assert source.decode() == observer['allocator']((root / 'commercial-allocator-015/buffer-vdi.cpp').read_text())
binary = (root / 'commercial-allocator-073/libdisplay_buffer_vdi_impl.z.so').read_bytes()
assert hashlib.sha256(binary).hexdigest() == allocator['sha256']
assert allocator['original_commercial_runtime'] and allocator['allocator_return_values_unchanged']
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-072/initrd.img')
after = helpers['parse'](root / 'commercial61-native-073/initrd.img')
assert set(before) <= set(after)
changed = sorted(name for name in before if before[name] != after[name])
assert changed == ['init', 'native-target/bootstrap'], changed
added = set(after) - set(before)
assert added == {'native-target/allocator073', 'native-target/allocator073/libdisplay_buffer_vdi_impl.z.so'}
assert stat.S_ISDIR(after['native-target/allocator073'][0])
assert after['native-target/allocator073/libdisplay_buffer_vdi_impl.z.so'][1] == binary
assert all(before[name] == after[name] for name in before if name.startswith(
    ('native-target/software-codec072/', 'native-target/original-ui070/')))
overlay = json.loads((report / 'overlay-result.json').read_text())
parent = json.loads((b.parent / 'reports/commercial61-native-072/overlay-result-xz.json').read_text())
assert overlay['shared_parent_overlay_sha256'] == parent['sha256']
assert overlay['chain'] == ['commercial61-native-001/initrd.img', 'commercial61-native-017/initrd.img',
    'commercial61-native-016/initrd.img', 'commercial61-native-072/initrd.img', 'commercial61-native-073/initrd.img']
assert overlay['ordered_chain_equals_full_073']
result = dict(exact_observer_source_delta=True, all_other_existing_archive_members_unchanged=True,
    original_software_backend_unchanged=True, original_resource_files_unchanged=True,
    allocator_public_logging_only=True, allocator_return_values_unchanged=True,
    original_service_identities_unchanged=True, compiled_logger_tests_passed=True,
    shared_parent_chain_verified=True, readonly_overlays=True, existing_members_changed=changed,
    added_members=sorted(added), allocator_sha256=allocator['sha256'],
    public_metadata_only=True, private_memory_read=False, native_runtime_verified=False,
    desktop_verified=False, interaction_verified=False)
with (report / 'admission-test.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))

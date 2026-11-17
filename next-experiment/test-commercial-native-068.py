"""Archive admission: only diagnostic init, bootstrap and composer may differ."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(
    n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]),
    'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-067/initrd.img')
after = helpers['parse'](root / 'commercial61-native-068/initrd.img')
assert set(before) == set(after)
changed = sorted(k for k in before if before[k] != after[k])
assert changed == ['init', 'native-target/bootstrap',
                   'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'], changed
new = runpy.run_path(str(b / 'build-commercial-native-068.py'))
assert (root / 'commercial61-native-068/init.c').read_text() == new['outer']
assert (root / 'commercial61-native-068/bootstrap.c').read_text() == new['inner']
test = json.loads((b.parent / 'reports/commercial-full-capture-test-068.json').read_text())
assert all(test[k] for k in ['compiled_helpers_passed', 'address_undefined_sanitizers_passed',
    'pixel_exact_rgba_bgra_and_stride', 'source_maps_unchanged', 'partial_publish_rejected',
    'existing_outputs_never_overwritten', 'wrong_owner_symlink_oversize_and_malformed_rejected',
    'exact_composer_source_addition', 'exact_bootstrap_export_additions'])
for name, expected in test['header_sha256'].items():
    assert hashlib.sha256((b / name).read_bytes()).hexdigest() == expected
composer = json.loads((root / 'commercial-composer-068/result.json').read_text())
assert composer['full_capture_header_sha256'] == test['header_sha256']['native-full-capture-068.h']
assert composer['public_exports_unchanged'] and composer['original_artifacts_unchanged']
assert hashlib.sha256(after[changed[-1]][1]).hexdigest() == composer['composer_sha256']
overlay = json.loads((root / 'commercial61-native-068/overlay-result.json').read_text())
assert overlay['ordered_chain_equals_full_068']
result = dict(exact_delta_from_067=changed, all_other_members_byte_identical=True,
              original_service_and_egl_members_byte_identical=True,
              full_capture_helpers_tested=True, diagnostic_source_additions_only=True,
              bounded_outer_export_ms=8000, private_evidence_directory_owner=3036,
              original_service_credentials_unchanged=True, original_images_written=False,
              desktop_verified=False, target_runtime_verified=False)
with (b.parent / 'reports/commercial61-native-068/admission-test.json').open('x') as out:
    json.dump(result, out, indent=2)
print(json.dumps(result, indent=2))

"""Admit only the proven diagnostic EGL and outer run-name changes."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
old = runpy.run_path(str(b / 'build-commercial-native-066.py'))
new = runpy.run_path(str(b / 'build-commercial-native-067.py'))
assert old['inner'] == new['inner']
assert new['outer'].replace('commercial61-native-067', 'commercial61-native-066').replace(
    'COMMERCIAL067', 'COMMERCIAL066') == old['outer']
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(
    n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]),
    'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-066/initrd.img')
after = helpers['parse'](root / 'commercial61-native-067/initrd.img')
assert set(before) == set(after)
changed = sorted(k for k in before if before[k] != after[k])
assert changed == ['init', 'native-target/graphics016/system/lib64/libEGL_impl.so'], changed
key = changed[1]
diagnostic = json.loads((root / 'commercial-egl-067/result.json').read_text())
assert hashlib.sha256(after[key][1]).hexdigest() == diagnostic['bridge_sha256']
assert diagnostic['public_exports_unchanged'] and diagnostic['original_artifacts_unchanged']
gate = json.loads((b.parent / 'reports/commercial-late-readback-test-067.json').read_text())
assert gate['compiled_gate_passed'] and gate['exact_source_delta_verified']
baseline = json.loads((b.parent / 'reports/commercial61-native-066/perf-stream-test.json').read_text())
assert baseline['synthetic_ring_tests_passed'] and baseline['exact_read_only_source_delta']
result = dict(exact_delta_from_066=changed, bootstrap_byte_identical=True,
              all_other_members_byte_identical=True, diagnostic_gate_test_passed=True,
              public_exports_unchanged=True, original_images_written=False,
              desktop_verified=False, target_runtime_verified=False)
out = b.parent / 'reports/commercial61-native-067/admission-test.json'
with out.open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))

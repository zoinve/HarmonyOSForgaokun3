"""Admit only the precise reference-dismissal and evidence delta over 074."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
report = b.parent / 'reports/commercial61-native-075'
test = json.loads((b.parent / 'reports/commercial-desktop-test-075/result.json').read_text())
assert all(test[key] for key in ['original_reference_commands_verified', 'mock_cli_control_flow_passed',
    'no_stop_when_services_or_guide_missing', 'stop_failure_not_misreported',
    'exact_composer_source_addition', 'two_independent_capture_directories', 'activation_state_not_modified'])
h = runpy.run_path(str(b / 'commercial-desktop-evidence-075.py'))
old = runpy.run_path(str(b / 'build-commercial-native-074.py'))
new = runpy.run_path(str(b / 'build-commercial-native-075.py'))
assert new['inner'] == h['inner'](old['inner']) and new['outer'] == h['outer'](old['outer'])
assert 'mount("overlay","/system","overlay",MS_RDONLY,options)' in new['inner']
assert 'mount("overlay","/vendor","overlay",MS_RDONLY,options)' in new['inner']
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))],
                      type_ignores=[]), 'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-074/initrd.img')
after = helpers['parse'](root / 'commercial61-native-075/initrd.img')
assert set(before) <= set(after)
changed = sorted(name for name in before if before[name] != after[name])
assert changed == ['init', 'native-target/bootstrap',
                   'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so']
assert set(after) - set(before) == {'native-target/commercial-direct-desktop-075.sh'}
assert hashlib.sha256(after['native-target/commercial-direct-desktop-075.sh'][1]).hexdigest() == test['script_sha256']
build = json.loads((root / 'commercial-composer-075/result.json').read_text())
assert hashlib.sha256(after[changed[-1]][1]).hexdigest() == build['composer_sha256']
assert build['source_sha256'] == test['composer_source_sha256']
overlay = json.loads((report / 'overlay-result.json').read_text())
parent = json.loads((b.parent / 'reports/commercial61-native-074/overlay-result.json').read_text())
assert overlay['chain'] == parent['chain'] + ['commercial61-native-075/initrd.img']
assert overlay['shared_parent_overlay_sha256'] == parent['sha256']
result = dict(exact_archive_delta=True, reference_commands_verified=True, activation_state_not_modified=True,
    original_service_identities_unchanged=True, readonly_overlays=True, shared_parent_chain_verified=True,
    second_capture_source_verified=True, changed_members=changed,
    added_members=sorted(set(after)-set(before)), original_account_script_unchanged=True,
    original_codec_resources_yuv_unchanged=True, desktop_verified=False, interaction_verified=False)
(report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
workflow = runpy.run_path(str(b / 'commercial-workflow-075.py'))
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return']:
    compile(workflow['source075'](name), name, 'exec')
print(json.dumps(result, indent=2))

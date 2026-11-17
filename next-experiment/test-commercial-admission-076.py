"""Prove exact init-managed service addition without changing original identities."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
report = b.parent / 'reports/commercial61-native-076'
module = runpy.run_path(str(b / 'commercial-init-desktop-076.py'))
old = runpy.run_path(str(b / 'build-commercial-native-075.py'))
new = runpy.run_path(str(b / 'build-commercial-native-076.py'))
assert new['inner'] == old['inner']
assert new['outer'] == old['outer'].replace('commercial61-native-075', 'commercial61-native-076').replace('COMMERCIAL075', 'COMMERCIAL076')
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))],
                      type_ignores=[]), 'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-075/initrd.img')
after = helpers['parse'](root / 'commercial61-native-076/initrd.img')
assert set(before) == set(after)
changed = sorted(name for name in before if before[name] != after[name])
assert changed == ['init', 'native-target/commercial-direct-desktop-075.sh', 'native-target/samgr_standard005.cfg']
config_key = 'native-target/samgr_standard005.cfg'
assert after[config_key][1] == module['update_config'](before[config_key][1])
old_config, new_config = json.loads(before[config_key][1]), json.loads(after[config_key][1])
assert new_config['services'][:-1] == old_config['services']
service = new_config['services'][-1]
assert service == module['CONFIG']['services'][0]
assert service['name'] == 'matebook_desktop076'
assert service['uid'] == 'root' and service['secon'] == 'u:r:sh:s0'
assert service['permission'] == ['ohos.permission.START_ABILITIES_FROM_BACKGROUND',
    'ohos.permission.GET_BUNDLE_INFO_PRIVILEGED', 'ohos.permission.KILL_APP_PROCESSES',
    'ohos.permission.CLEAN_BACKGROUND_PROCESSES', 'ohos.permission.DUMP']
assert set(service) == {'name','path','uid','gid','permission','secon','sandbox','once','start-mode'}
assert service['path'] == ['/system/bin/sh','-c',module['SCRIPT']]
assert after['native-target/commercial-direct-desktop-075.sh'][1] == b'#!/system/bin/sh\nexit 0\n'
assert after['native-target/bootstrap'] == before['native-target/bootstrap']
for token in ['param set', 'setuid', 'setgid', 'setcon', 'LD_PRELOAD', 'setenforce', 'ioctl', 'tokenid']:
    assert token not in module['SCRIPT'].lower()
overlay = json.loads((report / 'overlay-result.json').read_text())
parent = json.loads((b.parent / 'reports/commercial61-native-075/overlay-result.json').read_text())
assert overlay['chain'] == parent['chain'] + ['commercial61-native-076/initrd.img']
assert overlay['shared_parent_overlay_sha256'] == parent['sha256']
result = dict(exact_archive_delta=True, original_service_definitions_preserved=True,
    distinct_init_managed_service=True, no_supplied_token_or_activation_state=True,
    shared_parent_chain_verified=True, prior_preinit_caller_disabled=True,
    bootstrap_composer_allocator_egl_resources_unchanged=True, original_account_wrapper_unchanged=True,
    permissions_explicitly_requested_not_checks_disabled=True, changed_members=changed,
    service_name=service['name'], config_sha256=hashlib.sha256(after[config_key][1]).hexdigest(),
    init_issued_token_verified=False, guide_dismissal_verified=False, desktop_verified=False, interaction_verified=False)
(report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
workflow = runpy.run_path(str(b / 'commercial-workflow-076.py'))
for name in ['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']:
    compile(workflow['source076'](name), name, 'exec')
print(json.dumps(result, indent=2))

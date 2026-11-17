"""Validate the exact script-file correction and unchanged original runtime."""
from pathlib import Path
import ast
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
report = b.parent / 'reports/commercial61-native-077'
module = runpy.run_path(str(b / 'commercial-init-desktop-077.py'))
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))],
                      type_ignores=[]), 'archive-helpers', 'exec'), helpers)
before = helpers['parse'](root / 'commercial61-native-076/initrd.img')
after = helpers['parse'](root / 'commercial61-native-077/initrd.img')
script_key = 'native-target/commercial-desktop077.sh'
assert set(after) - set(before) == {script_key}
assert not set(before) - set(after)
changed = sorted(k for k in after if before.get(k) != after[k])
assert changed == ['init', script_key, 'native-target/samgr_standard005.cfg']
old_cfg = json.loads(before['native-target/samgr_standard005.cfg'][1])
cfg = json.loads(after['native-target/samgr_standard005.cfg'][1])
assert cfg['services'][:-1] == old_cfg['services'][:-1]
assert {k:v for k,v in cfg.items() if k != 'services'} == {k:v for k,v in old_cfg.items() if k != 'services'}
service = cfg['services'][-1]
assert service == module['CONFIG']['services'][0]
assert service['name'] == 'matebook_desktop077'
assert service['path'] == ['/system/bin/sh', '/commercial-desktop077.sh']
assert max(len(arg.encode()) for arg in service['path']) < 64
assert sum(len(arg.encode()) + 1 for arg in service['path']) < 128
assert after[script_key][1] == module['SCRIPT'].encode()
assert after[script_key][0] & 0o777 == 0o755
assert after['native-target/commercial-direct-desktop-075.sh'][1] == b'#!/system/bin/sh\nexit 0\n'
assert service['permission'] == old_cfg['services'][-1]['permission']
overlay = json.loads((report / 'overlay-result.json').read_text())
parent = json.loads((b.parent / 'reports/commercial61-native-076/overlay-result.json').read_text())
assert overlay['chain'] == parent['chain'] + ['commercial61-native-077/initrd.img']
assert overlay['shared_parent_overlay_sha256'] == parent['sha256']
result = dict(exact_archive_delta=True, original_service_definitions_preserved=True,
    distinct_init_managed_service=True, no_supplied_token_or_activation_state=True,
    shared_parent_chain_verified=True, prior_preinit_caller_disabled=True,
    bounded_argv_and_executable_script_verified=True, changed_members=changed,
    config_sha256=hashlib.sha256(after['native-target/samgr_standard005.cfg'][1]).hexdigest(),
    native_init_parser_acceptance_verified=False, init_issued_token_verified=False,
    guide_dismissal_verified=False, desktop_verified=False, interaction_verified=False)
(report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
workflow = runpy.run_path(str(b / 'commercial-workflow-077.py'))
for name in ['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']:
    compile(workflow['source077'](name), name, 'exec')
print(json.dumps(result, indent=2))

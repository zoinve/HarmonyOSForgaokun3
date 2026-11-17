"""Move guide commands from pre-init kernel context into their own init service."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-075.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-075', 'commercial61-native-076').replace('COMMERCIAL075', 'COMMERCIAL076')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-075', 'commercial61-native-076')
anchor = 'def member(name,mode,data,ino):'
addition = '''
module076=runpy.run_path(str(base/'commercial-init-desktop-076.py'))
key076='native-target/samgr_standard005.cfg'
mode076,before076=entries[key076]
entries[key076]=(mode076,module076['update_config'](before076))
# Disable the unsuccessful pre-init caller; do not change the bootstrap or an original service.
key076='native-target/commercial-direct-desktop-075.sh'
entries[key076]=(entries[key076][0],b'#!/system/bin/sh\\nexit 0\\n')
record076=dict(service=module076['CONFIG']['services'][0],
 original_config_sha256=hashlib.sha256(before076).hexdigest(),
 updated_config_sha256=hashlib.sha256(entries['native-target/samgr_standard005.cfg'][1]).hexdigest(),
 distinct_diagnostic_service=True,init_issues_token=True,no_existing_service_identity_changed=True,
 no_existing_permission_removed=True,no_token_value_supplied=True,activation_state_modified=False)
(local/'init-desktop-provenance.json').open('x').write(json.dumps(record076,indent=2))
'''
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

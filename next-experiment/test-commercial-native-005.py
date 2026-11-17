from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-005.py').is_file(),'missing original-context profile diagnostic candidate'
p=runpy.run_path(str(base/'build-commercial-native-005.py'));s=p['inner']
assert 'commercial_profile005();' in s and 'commercial-profile005/profile.log' in s
assert s.index('    commercial_profile005();')<s.index('    guest_permissive_config_047();')
assert 'samgr_standard005.cfg' in p['payload'] and 'commercial61-original-001/' in p['outer']
assert 'commercial61-native-005-%s' in p['outer'] and 'left033=420' in p['outer']
assert 'setuid(' not in s and 'setgid(' not in s
assert 'official-arm-sdk' not in s and 'graphics_egl054' not in s
print('PASS: original service credentials/config fields retained; only an observe-then-exec path, commercial images, bounded return')

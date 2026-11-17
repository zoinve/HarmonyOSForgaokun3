from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-006.py').is_file(),'missing chroot-correct observer sources'
p=runpy.run_path(str(base/'build-commercial-native-006.py'));s=p['inner']
assert 'commercial_copy005("/samgr-observe",' in s
assert 'commercial_copy005("/samgr_standard005.cfg",' in s
assert 'commercial_copy005("/native-target/' not in s
assert "entries['native-target/samgr-observe']" in p['payload']
assert 'commercial61-native-006-%s' in p['outer'] and 'commercial61-original-001/' in p['outer']
print('PASS: archive native-target members become root paths after the existing target chroot; identities and original images unchanged')

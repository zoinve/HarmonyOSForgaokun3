"""Read-only wiring and archive provenance, not a boot or graphics acceptance."""
from pathlib import Path
import runpy,ast
base=Path(__file__).resolve().parent
for name in ['install-commercial-native-016.py','run-commercial-native-016.py','retrieve-commercial-evidence-016.py']:
 assert (base/name).is_file(), 'missing unique 016 deployment wiring'
 p=runpy.run_path(str(base/name));s=p['source'];ast.parse(s)
 assert '10.126.126.14' in s and 'HostKeyAlias=192.168.10.128' in s
 assert 'reports/commercial61-native-016-r2' in s
 assert 'StrictHostKeyChecking=no' not in s
s=runpy.run_path(str(base/'install-commercial-native-016.py'))['source']
assert '/home/zoinve/harmony-virgl-883/commercial61-native-016-r2/' in s
assert "entry=esp/'loader/entries/commercial61-native-016.conf'" in s
assert "initrd /commercial61-native-001/initrd.img" in s
assert "initrd /commercial61-native-016/initrd.img" in s
assert '11*1024**3' in s and '32*1024**2' in s
print('PASS: 016 operational ID, preserved r2 build evidence, trusted address, memory and EFI guards')

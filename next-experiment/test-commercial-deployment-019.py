"""Read-only wiring checks; never invokes installation or reboot."""
from pathlib import Path
import runpy,ast
base=Path(__file__).resolve().parent
assert (base/'install-commercial-native-019.py').is_file(),'missing 019 deployment wiring'
s=runpy.run_path(str(base/'install-commercial-native-019.py'))['source']
ast.parse(s)
for n in ['001','017','016','019']:assert 'initrd /commercial61-native-'+n+'/initrd.img' in s
assert '30*1024**2' in s and '31*1024**2' not in s
assert 'HostKeyAlias=192.168.10.128' in s and 'HostName=10.126.126.14' in s
assert 'StrictHostKeyChecking=no' not in s
assert 'commercial61-original-001' in s
assert 'is-active' in s and 'inactive' in s
print('PASS: guarded original-image chain, trusted connection and explicit 30 MiB reserve')

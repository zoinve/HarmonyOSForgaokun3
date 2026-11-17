"""Deployment wiring only; does not perform target operations."""
from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
for name in ['build-commercial-overlay-010.py','install-commercial-native-010.py','run-commercial-native-010.py']:
 assert (b/name).is_file(), 'missing guarded 010 deployment: '+name
s=runpy.run_path(str(b/'install-commercial-native-010.py'))['source']
assert 'HostName=10.126.126.14' in s and 'HostKeyAlias=192.168.10.128' in s
assert 'AUTO RETURN 210 SEC' in s and 'AUTO RETURN 7 MIN' not in s
assert "mem['MemAvailable']>=11*1024**3" in s
assert "'inactive'" in s and "'disabled'" in s
assert "'initrd /commercial61-native-001/initrd.img','initrd /commercial61-native-010/initrd.img'" in s
r=runpy.run_path(str(b/'run-commercial-native-010.py'))['source']
assert 'HostName=10.126.126.14' in r and 'mem[\'MemAvailable\']>=11*1024**3' in r
assert 'ubuntu_online_only_pending_guest_exit_evidence' in r
assert 'StrictHostKeyChecking=no' not in s+r
print('PASS: 010 new-address trusted-key connection, fresh RAM admission, disabled timer and unique bounded entry wiring; no target actions')

"""Assembled source only; never installs or boots the target."""
from pathlib import Path
import runpy,ast
b=Path(__file__).resolve().parent
assert (b/'install-commercial-native-017.py').is_file(),'missing guarded 017 four-initrd deployment'
s=runpy.run_path(str(b/'install-commercial-native-017.py'))['source'];ast.parse(s)
assert "'initrd /commercial61-native-001/initrd.img','initrd /commercial61-native-017/initrd.img','initrd /commercial61-native-016/initrd.img','initrd /commercial61-native-017/initrd.img'" in s
assert "sha(esp/'commercial61-native-016/initrd.img')=='3c620a7e8501648fc55589ee93d3a5afadc1e07d7b6c54b79a24c6f495837ae9'" in s
assert '31*1024**2' in s and 'HostKeyAlias=192.168.10.128' in s
assert 'HostName=10.126.126.14' in s and '11*1024**3' in s
assert 'StrictHostKeyChecking=no' not in s
print('PASS: ordered existing hardware reuse, explicit directories, guarded identity/memory/address, 31 MiB EFI reserve')

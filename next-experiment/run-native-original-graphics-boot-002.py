"""Exactly one 002 boot; restore prior read-only LAB mount before collecting."""
from pathlib import Path

source=Path(__file__).with_name('run-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-002')
source=source.replace('native-original-graphics-001','native-original-graphics-002')
source=source.replace('native-original-001-','native-original-002-')
anchor="mount=cmd(['findmnt','-n','-o','SOURCE,OPTIONS','--target','/mnt/harmony-lab']).strip()"
assert source.count(anchor)==1
source=source.replace(anchor,'''import os
lab=Path('/mnt/harmony-lab')
if not os.path.ismount(lab):
 assert lab.is_dir() and not lab.is_symlink() and not any(lab.iterdir())
 assert cmd(['blkid','-s','UUID','-o','value','/dev/nvme0n1p4']).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
 assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p4']).strip()=='24bd14b9-9d92-490a-ad15-a59c6b8e7cd9'
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nosuid,nodev,noexec','/dev/nvme0n1p4',str(lab)],check=True)
'''+anchor)
source=source.replace('efi_files_verified_unchanged=79',
                      'efi_files_verified_unchanged=len(j[\'efi_before\'])-len(deleted)-len(mutable_boot_files)')
if __name__ == '__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

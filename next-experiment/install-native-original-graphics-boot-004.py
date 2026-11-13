"""Counted one-shot candidate; reclaim one obsolete duplicate EFI cache only."""
from pathlib import Path
source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-004')
source=source.replace('native-original-graphics-001','native-original-graphics-004')
source=source.replace('native trial 001','native trial 004')
old="obsolete=[esp/f'harmony-native-diag-{n}/linux' for n in ['009','010']]"
new="""retained=Path('/mnt/harmony-lab/work/native-diagnostic-init-007/diagnostic-init.cpio.gz')
assert retained.is_file() and not retained.is_symlink()
assert sha(retained)=='d0a16f3db2fcc42837783ca704fa6cfd448b301a84c1bdb96fc24f0b4e887bb2'
obsolete=[esp/'harmony-native-diag-007/initrd.img']"""
assert old in source
source=source.replace(old,new).replace('and sha(p)==sha(kernel)','and sha(p)==sha(retained)')
source=source.replace('retained_identical_kernel=str(kernel)','retained_identical_kernel=str(kernel),retained_identical_initrd=str(retained)')
# Historical result key retained for the runner; journal records the actual path.
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

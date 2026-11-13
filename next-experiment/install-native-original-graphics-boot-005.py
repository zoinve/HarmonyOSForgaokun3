"""Install a counted trial; reclaim only a retained obsolete EFI cache copy."""
from pathlib import Path
source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-005')
source=source.replace('native-original-graphics-001','native-original-graphics-005')
source=source.replace('native trial 001','native trial 005')
old="obsolete=[esp/f'harmony-native-diag-{n}/linux' for n in ['009','010']]"
new="""retained=Path('/mnt/harmony-lab/work/native-identity-diagnostic-008/diagnostic-init.cpio.gz')
assert retained.is_file() and not retained.is_symlink()
assert sha(retained)=='58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe'
obsolete=[esp/'harmony-native-diag-008/initrd.img']"""
assert old in source
source=source.replace(old,new).replace('and sha(p)==sha(kernel)','and sha(p)==sha(retained)')
source=source.replace('retained_identical_kernel=str(kernel)','retained_identical_kernel=str(kernel),retained_identical_initrd=str(retained)')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

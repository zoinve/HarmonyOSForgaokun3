"""Reuse retained kernel; remove only a verified obsolete duplicate cache."""
from pathlib import Path
source=Path(__file__).with_name('install-native-original-graphics-boot-005.py').read_text()
source=source.replace('boot-005','boot-006').replace('graphics-005','graphics-006').replace('trial 005','trial 006')
source=source.replace('diagnostic-008','diagnostic-009').replace('diag-008','diag-009').replace('58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe','c249d700d67c14dbd3c97182a823c14ecd9dde3102a9ff9aae358576f20b1d4c')
source=source.replace("obsolete=[esp/'harmony-native-diag-009/initrd.img']", """retained2=Path('/mnt/harmony-lab/work/native-identity-diagnostic-010/diagnostic-init.cpio.gz')
assert retained2.is_file() and not retained2.is_symlink() and sha(retained2)=='f00ae673e495abbd521628418badbc16d7f12d72d40236855b0a7f149e0e5afb'
obsolete=[esp/'harmony-native-diag-009/initrd.img',esp/'harmony-native-diag-010/initrd.img']""")
source=source.replace("and sha(p)==sha(retained)",'and sha(p)==sha(retained if p.parent.name.endswith("009") else retained2)')
source=source.replace('retained_identical_initrd=str(retained)', 'retained_identical_initrd=str(retained),retained_second_initrd=str(retained2)')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

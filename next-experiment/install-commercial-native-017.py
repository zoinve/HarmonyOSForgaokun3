"""Add 349 KiB only; directories bracket immutable 016 hardware archive."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-017').replace('8 GiB data and bounded return 010','Native graphics archive fix 017')
old="'initrd /commercial61-native-001/initrd.img','initrd /commercial61-native-017/initrd.img'"
new="'initrd /commercial61-native-001/initrd.img','initrd /commercial61-native-017/initrd.img','initrd /commercial61-native-016/initrd.img','initrd /commercial61-native-017/initrd.img'"
assert source.count(old)==1
source=source.replace(old,new,1)
anchor="assert sha(esp/'commercial61-native-001/initrd.img')=='f90233a25f0609c4a23f5a5168cffe2efa1cc1f20d00f2966cef0e1be00fa148'"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\nassert sha(esp/'commercial61-native-016/initrd.img')=='3c620a7e8501648fc55589ee93d3a5afadc1e07d7b6c54b79a24c6f495837ae9'",1)
# No old images deleted: leave at least 31 MiB after the small new overlay.
assert source.count('32*1024**2')==1
source=source.replace('32*1024**2','31*1024**2',1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Correct desktop CLI arguments; restore 32 MiB reserve after authorized EFI cleanup."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-020.py')))['source']
source=source.replace('commercial61-native-020','commercial61-native-021').replace('Reference desktop startup order 020','Reference aa arguments 021')
assert source.count('29*1024**2')==1
source=source.replace('29*1024**2','32*1024**2',1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

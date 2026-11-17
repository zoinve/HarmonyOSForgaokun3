"""Reference-aligned desktop start; explicit 29 MiB EFI reserve, no historical deletions."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-019.py')))['source']
source=source.replace('commercial61-native-019','commercial61-native-020').replace('Original seccomp library path alias 019','Reference desktop startup order 020')
assert source.count('30*1024**2')==1
source=source.replace('30*1024**2','29*1024**2',1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

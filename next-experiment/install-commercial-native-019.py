"""Add a narrow sandbox alias candidate; retain old evidence and original images.

The new 703455-byte overlay uses an explicit 30 MiB EFI reserve (formerly 31).
No historical files are deleted to make room.
"""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-018.py')))['source']
source=source.replace('commercial61-native-018','commercial61-native-019').replace('Original AppSpawn launcher 018','Original seccomp library path alias 019')
assert source.count('31*1024**2')==1
source=source.replace('31*1024**2','30*1024**2',1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

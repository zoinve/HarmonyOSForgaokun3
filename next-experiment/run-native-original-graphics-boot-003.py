"""Exactly one 003 boot; all original images checked before and after."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-002.py')))['source']
source=source.replace('native-original-graphics-boot-002','native-original-graphics-boot-003')
source=source.replace('native-original-graphics-002','native-original-graphics-003')
source=source.replace('native-original-002-','native-original-003-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

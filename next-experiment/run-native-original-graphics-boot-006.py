"""Exactly one counted physical trial and evidence collection."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-005.py')))['source']
source=source.replace('native-original-graphics-boot-005','native-original-graphics-boot-006').replace('native-original-graphics-005','native-original-graphics-006').replace('native-original-005-','native-original-006-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

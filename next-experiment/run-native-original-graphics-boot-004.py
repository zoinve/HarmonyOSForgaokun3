"""Exactly one native 004 trial, automatic Ubuntu return and raw evidence capture."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-002.py')))['source']
source=source.replace('native-original-graphics-boot-002','native-original-graphics-boot-004')
source=source.replace('native-original-graphics-002','native-original-graphics-004')
source=source.replace('native-original-002-','native-original-004-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

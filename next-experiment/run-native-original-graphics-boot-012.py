"""One guarded physical trial, then collect untouched evidence and Ubuntu state."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-011.py')))['source']
source=source.replace('native-original-graphics-boot-011','native-original-graphics-boot-012').replace('native-original-graphics-011','native-original-graphics-012').replace('native-original-011-','native-original-012-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

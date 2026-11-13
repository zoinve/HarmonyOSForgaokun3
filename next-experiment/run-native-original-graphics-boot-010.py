"""One bounded physical trial and evidence collection."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-009.py')))['source']
source=source.replace('native-original-graphics-boot-009','native-original-graphics-boot-010').replace('native-original-graphics-009','native-original-graphics-010').replace('native-original-009-','native-original-010-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

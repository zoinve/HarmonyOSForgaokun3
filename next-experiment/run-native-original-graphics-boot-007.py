"""One physical trial and immutable evidence collection."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-006.py')))['source']
source=source.replace('native-original-graphics-boot-006','native-original-graphics-boot-007').replace('native-original-graphics-006','native-original-graphics-007').replace('native-original-006-','native-original-007-')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

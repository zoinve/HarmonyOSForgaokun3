"""One new 017 attempt only; no retry and no changes to historical 016."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-017')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

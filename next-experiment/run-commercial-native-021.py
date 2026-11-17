"""One bounded boot with unchanged memory admission and original userland."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-020.py')))['source'].replace('commercial61-native-020','commercial61-native-021')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""One bounded test; network return alone is not proof of a desktop or auto-exit."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-019')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

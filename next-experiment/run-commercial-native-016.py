"""One authorized 016 attempt; no retry, conservative return classification."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-016')
source=source.replace("/'reports/commercial61-native-016'","/'reports/commercial61-native-016-r2'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

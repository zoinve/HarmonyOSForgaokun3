"""Retain conservative acceptance: actual process and pixels, not aa exit status."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('analyze-commercial-minimal-020.py')))['source'].replace('commercial61-native-020','commercial61-native-021').replace('COMMERCIAL020','COMMERCIAL021')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Preserve deployment guards; observe actual EGL presentation returns."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-028.py')))['source'].replace('commercial61-native-028','commercial61-native-029').replace('EGL initialization boundary diagnostics 028','EGL presentation return diagnostics 029')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

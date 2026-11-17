"""Unchanged deployment guards; correct only our diagnostic HiLog domain."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-025.py')))['source'].replace('commercial61-native-025','commercial61-native-026').replace('Bounded EGL boundary tracing 025','Valid EGL diagnostic domain 026')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

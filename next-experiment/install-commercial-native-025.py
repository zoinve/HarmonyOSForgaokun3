"""Retain standard Ubuntu return and original image/screen-off guards."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-024.py')))['source'].replace('commercial61-native-024','commercial61-native-025').replace('Local EGL bridge binding 024','Bounded EGL boundary tracing 025')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

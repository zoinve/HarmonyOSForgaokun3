"""Only diagnostic overlay installation, preserving the standard Ubuntu return."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-030.py')))['source'].replace('commercial61-native-030','commercial61-native-031').replace('Fresh source and scanout evidence 030','EGL source destination pixels 031')
source=source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-031-r2/','/home/zoinve/harmony-virgl-883/commercial61-native-031/')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

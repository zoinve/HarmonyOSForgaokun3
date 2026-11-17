"""Retain all deployment guards and original images; install fresh frame evidence."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-029.py')))['source'].replace('commercial61-native-029','commercial61-native-030').replace('EGL presentation return diagnostics 029','Fresh source and scanout evidence 030')
source=source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-030/','/home/zoinve/harmony-virgl-883/commercial61-native-030-r2/')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

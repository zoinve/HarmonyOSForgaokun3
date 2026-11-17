from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-031.py')))['source'].replace('commercial61-native-031','commercial61-native-032').replace('EGL source destination pixels 031','Bounded original desktop launch 032')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

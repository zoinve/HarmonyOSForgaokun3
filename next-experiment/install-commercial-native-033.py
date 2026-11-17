from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-032.py')))['source'].replace('commercial61-native-032','commercial61-native-033').replace('Bounded original desktop launch 032','Public GL dispatch observation 033')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

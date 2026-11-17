"""One 016 hardware candidate; r2 is the preserved successful build attempt."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-010.py')))['source']
source=source.replace('commercial61-native-010','commercial61-native-016').replace('8 GiB data and bounded return 010','MateBook native graphics 016')
source=source.replace("report=base/'reports/commercial61-native-016'","report=base/'reports/commercial61-native-016-r2'")
source=source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-016/','/home/zoinve/harmony-virgl-883/commercial61-native-016-r2/')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

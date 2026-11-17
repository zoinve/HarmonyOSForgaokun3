from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('verify-commercial-return-027.py')))['source'].replace('commercial61-native-027','commercial61-native-028')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

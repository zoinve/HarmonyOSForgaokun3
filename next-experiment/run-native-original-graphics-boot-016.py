from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-015.py')))['source']
source=source.replace('native-original-graphics-boot-015','native-original-graphics-boot-016').replace('native-original-graphics-015','native-original-graphics-016').replace('native-original-015-','native-original-016-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

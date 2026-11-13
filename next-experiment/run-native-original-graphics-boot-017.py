from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-016.py')))['source']
source=source.replace('native-original-graphics-boot-016','native-original-graphics-boot-017').replace('native-original-graphics-016','native-original-graphics-017').replace('native-original-016-','native-original-017-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

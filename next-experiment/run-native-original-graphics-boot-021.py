from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-020.py')))['source']
source=source.replace('native-original-graphics-boot-020','native-original-graphics-boot-021').replace('native-original-graphics-020','native-original-graphics-021').replace('native-original-020-','native-original-021-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

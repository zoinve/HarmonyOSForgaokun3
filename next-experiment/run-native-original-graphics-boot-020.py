from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-019.py')))['source']
source=source.replace('native-original-graphics-boot-019','native-original-graphics-boot-020').replace('native-original-graphics-019','native-original-graphics-020').replace('native-original-019-','native-original-020-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-014.py')))['source']
source=source.replace('native-original-graphics-boot-014','native-original-graphics-boot-015').replace('native-original-graphics-014','native-original-graphics-015').replace('native-original-014-','native-original-015-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

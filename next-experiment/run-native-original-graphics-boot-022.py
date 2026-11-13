from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-021.py')))['source']
source=source.replace('native-original-graphics-boot-021','native-original-graphics-boot-022').replace('native-original-graphics-021','native-original-graphics-022').replace('native-original-021-','native-original-022-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

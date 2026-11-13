from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-022.py')))['source']
source=source.replace('native-original-graphics-boot-022','native-original-graphics-boot-023').replace('native-original-graphics-022','native-original-graphics-023').replace('native-original-022-','native-original-023-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

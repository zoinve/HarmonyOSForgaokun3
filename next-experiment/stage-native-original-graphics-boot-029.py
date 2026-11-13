from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-027.py')))['source']
source=source.replace('native-original-graphics-boot-027','native-original-graphics-boot-029')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

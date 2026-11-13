from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-030.py')))['source']
source=source.replace('native-original-graphics-boot-030','native-original-graphics-boot-031')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

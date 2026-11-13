from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-024.py')))['source']
source=source.replace('native-original-graphics-boot-024','native-original-graphics-boot-025').replace('native-original-graphics-024','native-original-graphics-025').replace('native-original-024-','native-original-025-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

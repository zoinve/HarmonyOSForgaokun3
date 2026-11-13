from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-025.py')))['source']
source=source.replace('native-original-graphics-boot-025','native-original-graphics-boot-026').replace('native-original-graphics-025','native-original-graphics-026').replace('native-original-025-','native-original-026-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

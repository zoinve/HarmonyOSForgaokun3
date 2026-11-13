from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-026.py')))['source'].replace('native-original-graphics-boot-026','native-original-graphics-boot-027').replace('native-original-graphics-026','native-original-graphics-027').replace('native-original-026-','native-original-027-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

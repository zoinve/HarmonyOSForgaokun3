from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('run-native-original-graphics-boot-023.py')))['source']
source=source.replace('native-original-graphics-boot-023','native-original-graphics-boot-024').replace('native-original-graphics-023','native-original-graphics-024').replace('native-original-023-','native-original-024-')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

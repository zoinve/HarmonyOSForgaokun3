from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-017.py')))['source']
source=source.replace('native-original-graphics-boot-017','native-original-graphics-boot-018')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

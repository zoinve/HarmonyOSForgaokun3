from pathlib import Path
source=Path(__file__).with_name('stage-native-original-graphics-boot-035.py').read_text().replace('native-original-graphics-boot-035','native-original-graphics-boot-041')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

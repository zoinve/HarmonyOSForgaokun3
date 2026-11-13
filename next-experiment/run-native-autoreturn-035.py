from pathlib import Path
source=Path(__file__).with_name('run-native-autoreturn-033.py').read_text().replace('native-original-graphics-boot-033','native-original-graphics-boot-035').replace('native-original-graphics-033','native-original-graphics-035')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

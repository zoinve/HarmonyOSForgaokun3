from pathlib import Path
source=Path(__file__).with_name('install-native-render-overlay-034.py').read_text().replace('native-original-graphics-boot-034','native-original-graphics-boot-041').replace('native-original-graphics-034','native-original-graphics-041').replace('HarmonyOS 034 - NEON render','HarmonyOS 041 - GPU pipeline')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-024.py')))['source']
source=source.replace('native-original-graphics-boot-024','native-original-graphics-boot-025').replace('native-original-graphics-024','native-original-graphics-025').replace('trial 023','trial 025')
source=source.replace('native-original-graphics-boot-014/initrd.img','native-original-graphics-boot-015/initrd.img').replace('native-original-graphics-014/initrd.img','native-original-graphics-015/initrd.img').replace('4038119ad300d58e5079790197825f7f5110486aa629fa65989aa2082e54072b','077511f56a501c604809e2a3b831b0a4ec708ea4c3ff3da5e0352e43b11395ef')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

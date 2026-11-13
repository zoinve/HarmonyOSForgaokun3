from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-023.py')))['source']
source=source.replace('native-original-graphics-boot-023','native-original-graphics-boot-024').replace('native-original-graphics-023','native-original-graphics-024')
source=source.replace('native-original-graphics-boot-013/initrd.img','native-original-graphics-boot-014/initrd.img').replace('native-original-graphics-013/initrd.img','native-original-graphics-014/initrd.img').replace('2514452d557333d6665b20f9162c6fb2a43971f99fde720156bbda4f3623e333','4038119ad300d58e5079790197825f7f5110486aa629fa65989aa2082e54072b')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

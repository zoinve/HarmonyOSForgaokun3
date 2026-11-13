from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-026.py')))['source']
source=source.replace('native-original-graphics-boot-026','native-original-graphics-boot-027').replace('native-original-graphics-026','native-original-graphics-027').replace('trial 026','trial 027')
source=source.replace('native-original-graphics-boot-016/initrd.img','native-original-graphics-boot-018/initrd.img').replace('native-original-graphics-016/initrd.img','native-original-graphics-018/initrd.img').replace('c7225bfe3c1185e04b9b36346245647981a6e763ed835b809e767cef0e6bb5f9','630e074a61073ee461e3c7b297de4046ffde3a4a7009a3f5173738cbecd1a933')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

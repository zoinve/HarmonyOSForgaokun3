from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-018.py')))['source']
source=source.replace('native-original-graphics-boot-018','native-original-graphics-boot-019').replace('native-original-graphics-018','native-original-graphics-019').replace('trial 018','trial 019')
source=source.replace('native-original-graphics-boot-007/initrd.img','native-original-graphics-boot-008/initrd.img').replace('native-original-graphics-007/initrd.img','native-original-graphics-008/initrd.img').replace('a2e2ce801d82f1e05b52d6becf1f1bbfb53c036df664aede004824ee39955a64','c5ec21ba8821eb20100cb43c6e88cb903a2bdfd4ebe20a6bd181608f73c3e0f0')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

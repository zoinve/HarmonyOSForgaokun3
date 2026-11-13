from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-019.py')))['source']
source=source.replace('native-original-graphics-boot-019','native-original-graphics-boot-020').replace('native-original-graphics-019','native-original-graphics-020').replace('trial 019','trial 020')
source=source.replace('native-original-graphics-boot-008/initrd.img','native-original-graphics-boot-009/initrd.img').replace('native-original-graphics-008/initrd.img','native-original-graphics-009/initrd.img').replace('c5ec21ba8821eb20100cb43c6e88cb903a2bdfd4ebe20a6bd181608f73c3e0f0','4dc0a22ffbe37bbc0e3e63f5fd8e95a5c9f045ede2db026946646d75ce424868')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

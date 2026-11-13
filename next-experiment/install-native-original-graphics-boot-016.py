"""Reclaim only completed005's verified unreferenced EFI duplicate."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-015.py')))['source']
source=source.replace('native-original-graphics-boot-015','native-original-graphics-boot-016').replace('native-original-graphics-015','native-original-graphics-016').replace('trial 015','trial 016')
source=source.replace('native-original-graphics-boot-004/initrd.img','native-original-graphics-boot-005/initrd.img').replace('native-original-graphics-004/initrd.img','native-original-graphics-005/initrd.img').replace('c89db582260781c6da5f2781f395e5e1d4cfddbbdcbed245fc352676fa398032','f6a6f95fdd27bec6fd83d6c4267b39d6f6dde3e8980e1e983414032a82b51d3c')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

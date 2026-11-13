"""Reclaim only completed006's verified unreferenced EFI duplicate."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-016.py')))['source']
source=source.replace('native-original-graphics-boot-016','native-original-graphics-boot-017').replace('native-original-graphics-016','native-original-graphics-017').replace('trial 016','trial 017')
source=source.replace('native-original-graphics-boot-005/initrd.img','native-original-graphics-boot-006/initrd.img').replace('native-original-graphics-005/initrd.img','native-original-graphics-006/initrd.img').replace('f6a6f95fdd27bec6fd83d6c4267b39d6f6dde3e8980e1e983414032a82b51d3c','aa178dc25902d97b75e3efd94d3620a808c654e09eb8555ca85ab5d707ad851f')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

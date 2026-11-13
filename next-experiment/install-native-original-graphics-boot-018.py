"""Reclaim only completed007's verified unreferenced EFI duplicate."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-017.py')))['source']
source=source.replace('native-original-graphics-boot-017','native-original-graphics-boot-018').replace('native-original-graphics-017','native-original-graphics-018').replace('trial 017','trial 018')
source=source.replace('native-original-graphics-boot-006/initrd.img','native-original-graphics-boot-007/initrd.img').replace('native-original-graphics-006/initrd.img','native-original-graphics-007/initrd.img').replace('aa178dc25902d97b75e3efd94d3620a808c654e09eb8555ca85ab5d707ad851f','a2e2ce801d82f1e05b52d6becf1f1bbfb53c036df664aede004824ee39955a64')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Retain reserve by reclaiming only completed012's verified unreferenced EFI copy."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-017.py')))['source']
source=source.replace('native-original-graphics-boot-017','native-original-graphics-boot-022').replace('native-original-graphics-017','native-original-graphics-022').replace('trial 017','trial 022')
source=source.replace('native-original-graphics-boot-006/initrd.img','native-original-graphics-boot-012/initrd.img').replace('native-original-graphics-006/initrd.img','native-original-graphics-012/initrd.img').replace('aa178dc25902d97b75e3efd94d3620a808c654e09eb8555ca85ab5d707ad851f','6a74fc91774c6a1c7f7221a5a917e88c53bb59794bb79d6cd001291ff3ae47e2')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

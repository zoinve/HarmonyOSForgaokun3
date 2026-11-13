"""Reclaim only completed003's unreferenced EFI duplicate after retained-source hashing."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-013.py')))['source']
source=source.replace('native-original-graphics-boot-013','native-original-graphics-boot-014').replace('native-original-graphics-013','native-original-graphics-014').replace('trial 013','trial 014')
source=source.replace('native-original-graphics-boot-002/initrd.img','native-original-graphics-boot-003/initrd.img').replace('native-original-graphics-002/initrd.img','native-original-graphics-003/initrd.img').replace('94f5b22714cdcc0c554ac5350ca623c48954ac0f0b9b22ceb1fc2e64e73882df','2a9d4709ca860996ff48367e7e54ddb896dcd47e63c3de56b21f562ae0925600')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Retain completed002 originals; remove only its unreferenced EFI cache."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-012.py')))['source']
source=source.replace('native-original-graphics-boot-012','native-original-graphics-boot-013').replace('native-original-graphics-012','native-original-graphics-013').replace('trial 012','trial 013')
source=source.replace('native-original-graphics-boot-001/initrd.img','native-original-graphics-boot-002/initrd.img').replace('native-original-graphics-001/initrd.img','native-original-graphics-002/initrd.img').replace('490d046f9d1fd7067aab78f878c094f08760d23e8ad5e827d6a22bf69a4bbbc4','94f5b22714cdcc0c554ac5350ca623c48954ac0f0b9b22ceb1fc2e64e73882df')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

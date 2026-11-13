"""Reclaim only completed004's unreferenced EFI copy; retain source and evidence."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-014.py')))['source']
source=source.replace('native-original-graphics-boot-014','native-original-graphics-boot-015').replace('native-original-graphics-014','native-original-graphics-015').replace('trial 014','trial 015')
source=source.replace('native-original-graphics-boot-003/initrd.img','native-original-graphics-boot-004/initrd.img').replace('native-original-graphics-003/initrd.img','native-original-graphics-004/initrd.img').replace('2a9d4709ca860996ff48367e7e54ddb896dcd47e63c3de56b21f562ae0925600','c89db582260781c6da5f2781f395e5e1d4cfddbbdcbed245fc352676fa398032')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

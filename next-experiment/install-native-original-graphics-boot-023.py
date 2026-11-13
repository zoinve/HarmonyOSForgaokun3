"""Keep EFI reserve; reclaim only unreferenced013's verified duplicate payload."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-022.py')))['source']
source=source.replace('native-original-graphics-boot-022','native-original-graphics-boot-023').replace('native-original-graphics-022','native-original-graphics-023').replace('trial 022','trial 023')
source=source.replace('native-original-graphics-boot-012/initrd.img','native-original-graphics-boot-013/initrd.img').replace('native-original-graphics-012/initrd.img','native-original-graphics-013/initrd.img').replace('6a74fc91774c6a1c7f7221a5a917e88c53bb59794bb79d6cd001291ff3ae47e2','2514452d557333d6665b20f9162c6fb2a43971f99fde720156bbda4f3623e333')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Install without deleting any prior EFI files."""
from pathlib import Path
source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace("obsolete=[esp/f'harmony-native-diag-{n}/linux' for n in ['009','010']]",'obsolete=[]')
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-009').replace('native-original-graphics-001','native-original-graphics-009').replace('trial 001','trial 009')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

"""Reclaim only the unreferenced, retained byte-identical completed001 EFI initrd."""
from pathlib import Path
source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-012').replace('native-original-graphics-001','native-original-graphics-012').replace('trial 001','trial 012')
source=source.replace("obsolete=[esp/f'harmony-native-diag-{n}/linux' for n in ['009','010']]","""retained=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001/initrd.img')
assert sha(retained)=='490d046f9d1fd7067aab78f878c094f08760d23e8ad5e827d6a22bf69a4bbbc4'
obsolete=[esp/'native-original-graphics-001/initrd.img']""")
source=source.replace('sha(p)==sha(kernel)','sha(p)==sha(retained)')
source=source.replace("assert not any('/'+str(p.parent.relative_to(esp))+'/' in text for text in loader.values())","assert not any('/'+str(p.relative_to(esp)) in text.split() for text in loader.values())")
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

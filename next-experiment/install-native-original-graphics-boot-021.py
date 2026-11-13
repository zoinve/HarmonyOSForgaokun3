from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-020.py')))['source']
source=source.replace('native-original-graphics-boot-020','native-original-graphics-boot-021').replace('native-original-graphics-020','native-original-graphics-021').replace('trial 020','trial 021')
source=source.replace('native-original-graphics-boot-009/initrd.img','native-original-graphics-boot-010/initrd.img').replace('native-original-graphics-009/initrd.img','native-original-graphics-010/initrd.img').replace('4dc0a22ffbe37bbc0e3e63f5fd8e95a5c9f045ede2db026946646d75ce424868','3b70b22870b8aa7df888609cabb805937138a4d3fa378c91157aebb32d08dc3e')
old="""obsolete=[esp/'native-original-graphics-010/initrd.img']
for p in obsolete:
 assert not p.is_symlink() and not p.parent.is_symlink() and sha(p)==sha(retained)
 assert not any('/'+str(p.relative_to(esp)) in text.split() for text in loader.values())"""
new="""retained_011=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-011/initrd.img')
assert sha(retained_011)=='3acb1aa43e78973129af031cd6fa17d4641c1be78a02d816eb5600334d8df05c'
obsolete=[esp/'native-original-graphics-010/initrd.img',esp/'native-original-graphics-011/initrd.img']
for p,original in zip(obsolete,[retained,retained_011]):
 assert not p.is_symlink() and not p.parent.is_symlink() and sha(p)==sha(original)
 assert not any('/'+str(p.relative_to(esp)) in text.split() for text in loader.values())"""
assert source.count(old)==1
source=source.replace(old,new)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

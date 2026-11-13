"""Install manual entry only; never select or boot it."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-027.py')))['source']
source=source.replace('native-original-graphics-boot-027','native-original-graphics-boot-029').replace('native-original-graphics-027','native-original-graphics-029')
source=source.replace('title Harmony original-service native trial 027 (experimental)','title HarmonyOS 029 - Interactive NO AUTO REBOOT (volatile data)')
source=source.replace('native-original-graphics-029+1.conf','native-original-graphics-029.conf').replace('panic=30','panic=0')
# Reclaim only an unreferenced, byte-identical completed-trial EFI cache.
start=source.index("retained=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-018/initrd.img')")
end=source.index('assert shutil.disk_usage(esp).free+sum',start)
source=source[:start]+'''retained=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-019/initrd.img')
assert sha(retained)=='a491beb2882af60d972d0fa61a28080e7a60603883f16ef1df268f65ee656e40'
obsolete=[esp/'native-original-graphics-019/initrd.img']
for p in obsolete:
 assert not p.is_symlink() and not p.parent.is_symlink() and sha(p)==sha(retained)
 assert not any('/'+str(p.relative_to(esp)) in text.split() for text in loader.values())
'''+source[end:]
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

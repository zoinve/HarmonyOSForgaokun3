"""Install an uncounted manual capture entry, never select/reboot it."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-029.py')))['source']
source=source.replace('native-original-graphics-boot-029','native-original-graphics-boot-030').replace('native-original-graphics-029','native-original-graphics-030')
source=source.replace('HarmonyOS 029 - Interactive NO AUTO REBOOT (volatile data)','HarmonyOS 030 - NO AUTO REBOOT - persistent app crash capture')
source=source.replace('native-original-graphics-boot-019/initrd.img','native-original-graphics-boot-020/initrd.img').replace('native-original-graphics-019/initrd.img','native-original-graphics-020/initrd.img').replace('a491beb2882af60d972d0fa61a28080e7a60603883f16ef1df268f65ee656e40','f95e7b94055a83810b129f54267ee8c4870df135c9ae5e2325cd2817a9a17aea')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

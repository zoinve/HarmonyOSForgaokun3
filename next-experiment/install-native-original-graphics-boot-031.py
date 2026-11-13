"""Manual no-reboot entry with its OWN repaired kernel; shared kernel untouched."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-030.py')))['source']
source=source.replace('native-original-graphics-boot-030','native-original-graphics-boot-031').replace('native-original-graphics-030','native-original-graphics-031')
source=source.replace('HarmonyOS 030 - NO AUTO REBOOT - persistent app crash capture','HarmonyOS 031 - Binder PID FIX - NO AUTO REBOOT')
source=source.replace('native-original-graphics-boot-020/initrd.img','native-original-graphics-boot-021/initrd.img').replace('native-original-graphics-020/initrd.img','native-original-graphics-021/initrd.img').replace('f95e7b94055a83810b129f54267ee8c4870df135c9ae5e2325cd2817a9a17aea','02334578b5edea1ce2894f4fd70889accb881e0ae60a68f07ce9a419e5f4edfb')
assert source.count("assert sha(kernel)==sha(root/'linux')")==1
source=source.replace("assert sha(kernel)==sha(root/'linux')","assert sha(kernel)=='4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166'")
term="(root/'sc8280xp-huawei-gaokun3.dtb').stat().st_size+64*1024**2"
assert source.count(term)==2
source=source.replace(term,"(root/'sc8280xp-huawei-gaokun3.dtb').stat().st_size+(root/'linux').stat().st_size+64*1024**2")
anchor="options='rdinit=/init"
copy="""with (root/'linux').open('rb') as src,(dest/'linux').open('xb') as out:
 shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())
assert sha(dest/'linux')==sha(root/'linux')
"""
assert source.count(anchor)==1
source=source.replace(anchor,copy+anchor,1)
source=source.replace("'linux /harmony-native-diag-015/linux'","'linux /native-original-graphics-031/linux'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

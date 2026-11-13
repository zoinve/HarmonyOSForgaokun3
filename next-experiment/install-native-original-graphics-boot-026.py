"""Install candidate-local touch DT; preserve shared and Ubuntu device trees."""
from pathlib import Path
import runpy
source=runpy.run_path(str(Path(__file__).with_name('install-native-original-graphics-boot-025.py')))['source']
source=source.replace('native-original-graphics-boot-025','native-original-graphics-boot-026').replace('native-original-graphics-025','native-original-graphics-026').replace('trial 025','trial 026')
source=source.replace('native-original-graphics-boot-015/initrd.img','native-original-graphics-boot-016/initrd.img').replace('native-original-graphics-015/initrd.img','native-original-graphics-016/initrd.img').replace('077511f56a501c604809e2a3b831b0a4ec708ea4c3ff3da5e0352e43b11395ef','c7225bfe3c1185e04b9b36346245647981a6e763ed835b809e767cef0e6bb5f9')
old="assert sha(kernel)==sha(root/'linux') and sha(dtb)==sha(root/'sc8280xp-huawei-gaokun3.dtb')"
assert source.count(old)==1
source=source.replace(old,"assert sha(kernel)==sha(root/'linux')\nassert sha(dtb)=='2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32'")
source=source.replace("(root/'initrd.img').stat().st_size+64*1024**2","(root/'initrd.img').stat().st_size+(root/'sc8280xp-huawei-gaokun3.dtb').stat().st_size+64*1024**2")
anchor="assert sha(dest/'initrd.img')==sha(root/'initrd.img')"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\nwith (root/'sc8280xp-huawei-gaokun3.dtb').open('rb') as src,(dest/'sc8280xp-huawei-gaokun3.dtb').open('xb') as out:\n shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())\nassert sha(dest/'sc8280xp-huawei-gaokun3.dtb')==sha(root/'sc8280xp-huawei-gaokun3.dtb')")
source=source.replace("'devicetree /harmony-native-diag-015/sc8280xp-huawei-gaokun3.dtb'","'devicetree /native-original-graphics-026/sc8280xp-huawei-gaokun3.dtb'")
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

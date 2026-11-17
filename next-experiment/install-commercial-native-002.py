"""Add a small tested overlay, never replace the original commercial images."""
from pathlib import Path
source=Path(__file__).with_name('install-commercial-native-001.py').read_text()
source=source.replace('commercial61-native-001','commercial61-native-002')
source=source.replace("(report/'staged-original-images.json')","(base/'reports/commercial61-native-001/staged-original-images.json')")
source=source.replace("if item['name'] in ['init','bootstrap','initrd.img']:","if item['name'] in ['init','bootstrap']:")
anchor="code='payload='"
insert="""overlay=subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/commercial61-native-002/minimal-overlay.img'])
overlay_result=json.loads((report/'overlay-result.json').read_text())
assert hashlib.sha256(overlay).hexdigest()==overlay_result['sha256']
artifacts['initrd.img']=base64.b64encode(overlay).decode()
"""
assert source.count(anchor)==1
source=source.replace(anchor,insert+anchor,1)
anchor="images=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-original-001')"
source=source.replace(anchor,"assert sha(esp/'commercial61-native-001/initrd.img')=='f90233a25f0609c4a23f5a5168cffe2efa1cc1f20d00f2966cef0e1be00fa148'\n"+anchor,1)
source=source.replace("'initrd /commercial61-native-002/initrd.img'","'initrd /commercial61-native-001/initrd.img','initrd /commercial61-native-002/initrd.img'")
source=source.replace('commercial ISO - native probe','commercial ISO - minimal startup 002')
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})

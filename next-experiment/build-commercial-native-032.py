"""Keep observed rendering unchanged; bound normal desktop launch retries."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-031.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-031-%s','commercial61-native-032-%s').replace('COMMERCIAL031','COMMERCIAL032')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-031','commercial61-native-032')
anchor="patched=runpy.run_path(str(base/'commercial-desktop-order-021.py'))['repair'](original)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\npatched=runpy.run_path(str(base/'commercial-desktop-retry-032.py'))['repair'](patched)",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

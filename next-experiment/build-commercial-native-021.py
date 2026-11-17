"""Correct only the unsupported desktop CLI option; preserve the commercial image."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-020.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-020-%s','commercial61-native-021-%s').replace('COMMERCIAL020','COMMERCIAL021')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-020','commercial61-native-021')
assert payload.count("base/'commercial-desktop-order-020.py'")==1
payload=payload.replace("base/'commercial-desktop-order-020.py'","base/'commercial-desktop-order-021.py'",1)
# Keep the existing archive key and bootstrap copy path: only script contents change.
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

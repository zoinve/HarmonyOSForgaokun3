"""Same commercial board drivers as 016, with explicit archive directories."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-016.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-016-%s','commercial61-native-017-%s').replace('COMMERCIAL016','COMMERCIAL017')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-016-r2','commercial61-native-017')
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,"entries=runpy.run_path(str(base/'commercial-archive-017.py'))['complete'](entries)\n"+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

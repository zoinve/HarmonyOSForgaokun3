"""Resolve SceneBoard's two missing board-development mounts to real resources."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-021.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-021-%s','commercial61-native-022-%s').replace('COMMERCIAL021','COMMERCIAL022')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-021','commercial61-native-022')
anchor="alias=runpy.run_path(str(base/'commercial-app-sandbox-019.py'))['repair'](original)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\nalias=runpy.run_path(str(base/'commercial-sceneboard-mounts-022.py'))['repair'](alias)",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

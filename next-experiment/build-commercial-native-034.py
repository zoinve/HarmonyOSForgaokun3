"""Observe the original RenderService tree/screen through its public dump interface."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-033.py'))
inner=runpy.run_path(str(base/'commercial-rs-tree-034.py'))['instrument'](p['inner'])
outer=p['outer'].replace('commercial61-native-033-%s','commercial61-native-034-%s').replace('COMMERCIAL033','COMMERCIAL034')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-033','commercial61-native-034')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

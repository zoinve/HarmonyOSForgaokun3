"""Observe public frontend/Mesa GL state on the unchanged original service swap path."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-032.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-032-%s','commercial61-native-033-%s').replace('COMMERCIAL032','COMMERCIAL033')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-032','commercial61-native-033')
payload=payload.replace('commercial-egl-031','commercial-egl-033')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

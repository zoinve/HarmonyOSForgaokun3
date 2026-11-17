"""Observe own EGL copy source/destination; keep original service behavior."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-030.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-030-%s','commercial61-native-031-%s').replace('COMMERCIAL030','COMMERCIAL031')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-030','commercial61-native-031').replace("work=root/'commercial61-native-031-r2';","work=root/'commercial61-native-031';",1)
payload=payload.replace('commercial-egl-029','commercial-egl-031')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

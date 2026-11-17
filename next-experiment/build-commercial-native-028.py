"""Only our EGL diagnostic provider and unique run identifier change."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-027.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-027-%s','commercial61-native-028-%s').replace('COMMERCIAL027','COMMERCIAL028')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-027','commercial61-native-028').replace('commercial-egl-027','commercial-egl-028')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

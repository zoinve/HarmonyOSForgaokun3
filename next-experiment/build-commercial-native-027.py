"""Retain all original services; change only our diagnostic provider quotas."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-026.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-026-%s','commercial61-native-027-%s').replace('COMMERCIAL026','COMMERCIAL027')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-026','commercial61-native-027').replace('commercial-egl-026','commercial-egl-027')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

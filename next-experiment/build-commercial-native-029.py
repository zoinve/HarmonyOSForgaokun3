"""Preserve the bootstrap and original services; observe own EGL return values."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-028.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-028-%s','commercial61-native-029-%s').replace('COMMERCIAL028','COMMERCIAL029')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-028','commercial61-native-029').replace('commercial-egl-028','commercial-egl-029')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

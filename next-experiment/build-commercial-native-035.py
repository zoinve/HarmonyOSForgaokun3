"""Retain 033 bootstrap; do not repeat the known-denied 034 dump queries."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-033.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-033-%s','commercial61-native-035-%s').replace('COMMERCIAL033','COMMERCIAL035')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-033','commercial61-native-035')
payload=payload.replace('commercial-egl-033','commercial-egl-035')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

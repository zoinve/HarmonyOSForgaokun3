"""Same 024 base and 025 diagnostic boundaries, with a valid HiLog domain."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-025.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-025-%s','commercial61-native-026-%s').replace('COMMERCIAL025','COMMERCIAL026')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-025','commercial61-native-026').replace('commercial-egl-025','commercial-egl-026')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)

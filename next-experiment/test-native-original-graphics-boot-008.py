"""Early reader must wait for the original socket and survive startup races."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=base/'build-native-original-graphics-boot-008.py'
assert p.exists(),'startup reader retry missing'
d=runpy.run_path(str(p));assert 'hilogOutput",F_OK' in d['inner'] and 'NATIVE_HILOG008_RETRY' in d['inner']
t=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-008'),text=True,timeout=120).returncode)

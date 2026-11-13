"""Cover actual original screen initialization log tags."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=base/'build-native-original-graphics-boot-009.py'
assert p.exists(),'actual screen initialization log coverage missing'
d=runpy.run_path(str(p))
assert 'COMPOSER_SRV,Composer,RSScreenPreprocessor,RSScreenManager' in d['inner']
assert 'HdiBackend,HdiDevice' not in d['inner']
t=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-009'),text=True,timeout=120).returncode)

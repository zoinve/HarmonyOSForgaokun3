"""Trace real composer calls without replacing their results or credentials."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=base/'build-native-original-graphics-boot-006.py'
assert p.exists(),'composer boundary trace missing'
d=runpy.run_path(str(p))
assert '/data/native-composer-006.trace' in d['inner']
assert 'NATIVE_COMPOSER006' in d['instrument']
assert 'AuroraOpenDisplayDrm' in d['instrument']
old=runpy.run_path(str(base/'build-native-original-graphics-boot-005.py'))
assert d['outer']==old['outer'].replace('native-original-005-%s','native-original-006-%s')
t=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-006'),text=True,timeout=120).returncode)

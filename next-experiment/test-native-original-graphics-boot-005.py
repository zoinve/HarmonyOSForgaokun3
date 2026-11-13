"""Passive graphics diagnostics retain all native boot safety boundaries."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-005.py'
assert builder.is_file(), 'focused native graphics observation missing'
d=runpy.run_path(str(builder))
assert 'NATIVE_GRAPHICS005_FD' in d['inner']
assert '"-P",id,NULL' in d['inner']
assert '/sys/class/drm' in d['inner']
previous=runpy.run_path(str(base/'build-native-original-graphics-boot-004.py'))
assert d['outer']==previous['outer'].replace('native-original-004-%s','native-original-005-%s')
test=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
payload=test['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-005')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

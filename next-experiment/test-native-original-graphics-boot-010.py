"""Require actual target-only ashmem module installation before original init."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=base/'build-native-original-graphics-boot-010.py'
assert p.exists(),'original ashmem dependency repair missing'
d=runpy.run_path(str(p))
assert 'SYS_finit_module' in d['outer'] and 'NATIVE_ASHMEM010 loaded=1' in d['outer']
assert d['outer'].index('wrong_board')<d['outer'].index('SYS_finit_module')
assert 'file(\'hmos_ashmem.ko\'' in d['payload']
t=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-010'),text=True,timeout=120).returncode)

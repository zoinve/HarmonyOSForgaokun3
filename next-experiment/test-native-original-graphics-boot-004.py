"""Ensure private diagnostic umask never leaks into original service boot."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-004.py'
assert builder.is_file(), 'candidate 004 umask boundary fix missing'
d=runpy.run_path(str(builder))
child=d['outer'][d['outer'].index('static int native_child('):d['outer'].index('static int native_loop(')]
assert 'umask(022);' in child and child.index('umask(022);')<child.index('execve(')
assert 'umask(077);' in d['outer']
assert 'setns(rooted,CLONE_NEWNS)' in child
assert 'NATIVE_DAC004' in d['inner']
test=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
payload=test['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-004')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

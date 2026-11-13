"""Require a genuine rooted namespace, not chroot alone, before service boot."""
from pathlib import Path
import runpy

base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-003.py'
assert builder.is_file(), 'candidate 003 rooted namespace builder missing'
d=runpy.run_path(str(builder))
assert 'SYS_open_tree,AT_FDCWD,"/native-target",2|O_CLOEXEC|AT_RECURSIVE' in d['outer']
assert 'setns(rooted,CLONE_NEWNS)' in d['outer']
assert 'chroot(".")' not in d['outer'][d['outer'].index('static int native_child('):d['outer'].index('static int native_loop(')]
assert d['inner']==runpy.run_path(str(base/'build-native-original-graphics-boot-002.py'))['inner']
test=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
payload=test['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-003')
import subprocess
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

"""Ensure diagnostics cover library load and early original screen startup."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=base/'build-native-original-graphics-boot-007.py'
assert p.exists(),'early graphics boundary coverage missing'
d=runpy.run_path(str(p))
assert 'library_constructor' in d['payload'] and 'open("/dev/kmsg"' in d['payload']
assert 'COMPOSER_SRV,RSScreenManager' in d['inner']
t=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-007'),text=True,timeout=120).returncode)

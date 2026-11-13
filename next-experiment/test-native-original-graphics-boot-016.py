"""Require sparse RAM-only growth and genuine online ext4 resizing."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-016.py'
    assert path.exists(),'missing bounded RAM data expansion'
    p=runpy.run_path(str(path))
    assert 'ftruncate(ram,3221225472ULL)' in p['outer']
    assert '_IOW(\'f\',16,unsigned long long)' in p['inner']
    assert 'NATIVE_RAM_DATA016' in p['inner']
    assert p['capture']==p['p']['capture']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-016'),text=True,timeout=120).returncode)

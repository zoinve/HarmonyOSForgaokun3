"""Require bounded real target fault reports, not inferred crash identities."""
from pathlib import Path
import runpy, subprocess
base = Path(__file__).resolve().parent
if __name__ == '__main__':
    path = base / 'build-native-original-graphics-boot-018.py'
    assert path.exists(), 'missing target crash capture candidate'
    p = runpy.run_path(str(path))
    assert 'O_NOFOLLOW' in p['helper'] and 'fstatat' in p['helper']
    assert 'AT_SYMLINK_NOFOLLOW' in p['helper']
    assert 'NATIVE_FAULT018_HEX' in p['inner']
    assert '/data/log/faultlog' in p['inner']
    assert p['capture'] == p['p']['capture']
    old = runpy.run_path(str(base / 'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'], input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-018'), text=True, timeout=120).returncode)

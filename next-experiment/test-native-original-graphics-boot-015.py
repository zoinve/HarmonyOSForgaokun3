"""Require real SDK profile aliases without disabling original service sandboxes."""
from pathlib import Path
import runpy, subprocess
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-015.py'
    assert path.exists(),'missing native sandbox SDK layout compatibility'
    p=runpy.run_path(str(path));s=p['inner']
    assert 'symlink("/system",alias)' in s
    assert '"/mnt/sandbox/system","/mnt/sandbox/chipset"' in s
    assert s.index('NATIVE_LAYOUT015') < s.index('execve(arguments[0]')
    assert 'const.sandbox=disable' not in s
    assert p['capture']==p['p']['capture']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-015'),text=True,timeout=120).returncode)

"""Reject oversized hilog filters and unwritable UID3036 capture paths."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-013.py'
    assert path.exists(),'missing corrected passive diagnostics'
    p=runpy.run_path(str(path))
    tags=re.findall(r'"-T","([^"]+)"',p['inner'])
    assert tags and all(len(t.split(','))<=10 for t in tags),tags
    assert 'fchmod(capture_fd,0600)' in p['inner'] and 'fchown(capture_fd,3036,3036)' in p['inner']
    assert 'rename(' not in p['capture']
    assert 'scanout_capture_read_sync' in p['capture']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-013'),text=True,timeout=120).returncode)

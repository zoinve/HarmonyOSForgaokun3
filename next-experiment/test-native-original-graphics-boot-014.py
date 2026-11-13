"""Require passive original samgr profile visibility and valid early log coverage."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-014.py'
    assert path.exists(),'missing original samgr configuration diagnostics'
    p=runpy.run_path(str(path));s=p['inner']
    assert '/root/system/profile/installs.json' in s and '/environ' in s
    assert 'const.cust.config_dir_layer' in s
    assert all(len(t.split(','))<=10 for t in re.findall(r'"-T","([^"]+)"',s))
    assert p['capture']==p['p']['capture']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-014'),text=True,timeout=120).returncode)

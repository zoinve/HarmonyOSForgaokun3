"""Require bounded normal evdev input, not lock or authentication bypass."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
if __name__=='__main__':
    path=base/'build-native-original-graphics-boot-017.py'
    assert path.exists(),'missing real touch gesture candidate'
    p=runpy.run_path(str(path))
    assert 'Himax Capacitive TouchScreen' in p['inner']
    assert 'EVIOCGABS(ABS_MT_POSITION_Y)' in p['inner']
    assert 'input_event' in p['inner'] and 'ABS_MT_TRACKING_ID,-1' in p['inner']
    assert 'if(sample==8)native_swipe_017();' in p['inner']
    assert p['capture']==p['p']['capture']
    old=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=old.replace('native-original-graphics-boot-001','native-original-graphics-boot-017'),text=True,timeout=120).returncode)

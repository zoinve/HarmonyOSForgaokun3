from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-020.py').exists(),'missing explicit Bluetooth error-path trace candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-020.py'))
assert 'native-bt-020.trace' in p['inner']
assert 'NATIVE_BT020_TRACE' in p['inner']
assert 'fchmod(bt_trace,0666)' in p['inner']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-020')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

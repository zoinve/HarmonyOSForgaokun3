from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-022.py').exists(),'missing original-service QCA bridge candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-022.py'))
assert 'CLONE_NEWNET' in p['outer'] and 'native-qca-broker-022' in p['outer']
assert 'MS_BIND' in p['inner'] and '/native-bt-broker.sock' in p['inner']
assert 'native-qca-vendor-022.c' in p['payload']
assert 'qca-hci-reset' not in p['outer']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-022')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

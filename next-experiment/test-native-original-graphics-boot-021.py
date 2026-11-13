from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-021.py').exists(),'missing target QCA module and firmware candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-021.py'))
assert p['inner']==p['p']['inner']
assert 'qca-hci-reset' in p['outer'] and 'hci_uart' in p['outer']
assert p['outer'].index('NATIVE_ORIGINAL_REFUSED ubuntu_identity')<p['outer'].index('qca-hci-reset')
assert 'native-qca-firmware-021' in p['payload']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-021')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)

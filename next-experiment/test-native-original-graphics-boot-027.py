from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
assert (b/'build-native-original-graphics-boot-027.py').exists(),'missing normal-input settings diagnostic'
p=runpy.run_path(str(b/'build-native-original-graphics-boot-027.py'))
assert 'original_aa_start' not in p['inner']
assert 'KEY_LEFTMETA' in p['inner'] and 'KEY_I' in p['inner']
assert 'NATIVE_INPUT027_FD' in p['inner'] and 'HID 12d1:10b8 Keyboard' in p['inner']
t=runpy.run_path(str(b/'test-native-original-graphics-boot-001.py'))['payload']
t=t.replace('native-original-graphics-boot-001','native-original-graphics-boot-027')
raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=t,text=True,timeout=120).returncode)

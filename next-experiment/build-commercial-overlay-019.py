"""Keep immutable base/hardware archives; append the narrow app sandbox alias."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-018.py')))['payload']
payload=payload.replace('commercial61-native-018','commercial61-native-019')
anchor="'native-target/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh'}"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"'native-target/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh','native-target/appdata-sandbox019.json'}",1)
payload=payload.replace('ordered_chain_equals_full_018=True','ordered_chain_equals_full_019=True').replace('ordered 018 chain','ordered 019 chain')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

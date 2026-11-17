"""Append only new bootstrap/init and the two already bounded board-level fixes."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-019.py')))['payload']
payload=payload.replace('commercial61-native-019','commercial61-native-020')
anchor="'native-target/appdata-sandbox019.json'}"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"'native-target/appdata-sandbox019.json','native-target/desktop-order020.sh'}",1)
payload=payload.replace('ordered_chain_equals_full_019=True','ordered_chain_equals_full_020=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

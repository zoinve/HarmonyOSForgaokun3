"""Append corrected bootstrap/config only; retain original ordered hardware chain."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-022.py')))['payload']
payload=payload.replace('commercial61-native-022','commercial61-native-023').replace('ordered_chain_equals_full_022=True','ordered_chain_equals_full_023=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

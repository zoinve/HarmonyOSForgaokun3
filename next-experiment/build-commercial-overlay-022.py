"""Retain the existing verified base/directory/hardware chain, append only deltas."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-021.py')))['payload']
payload=payload.replace('commercial61-native-021','commercial61-native-022').replace('ordered_chain_equals_full_021=True','ordered_chain_equals_full_022=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

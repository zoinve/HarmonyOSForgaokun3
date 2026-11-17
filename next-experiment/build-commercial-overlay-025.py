"""Ordered minimal overlay containing only the new diagnostic provider delta."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-024.py')))['payload']
payload=payload.replace('commercial61-native-024','commercial61-native-025').replace('ordered_chain_equals_full_024=True','ordered_chain_equals_full_025=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

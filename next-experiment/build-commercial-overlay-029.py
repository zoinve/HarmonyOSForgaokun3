"""Validate ordered extraction and complete candidate equivalence."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-028.py')))['payload']
payload=payload.replace('commercial61-native-028','commercial61-native-029').replace('ordered_chain_equals_full_028=True','ordered_chain_equals_full_029=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

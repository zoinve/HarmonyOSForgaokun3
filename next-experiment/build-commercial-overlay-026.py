"""Verify the complete ordered archive, including the diagnostic provider delta."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-025.py')))['payload']
payload=payload.replace('commercial61-native-025','commercial61-native-026').replace('ordered_chain_equals_full_025=True','ordered_chain_equals_full_026=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

"""Only init and corrected desktop-start script differ from the current chain."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-020.py')))['payload']
payload=payload.replace('commercial61-native-020','commercial61-native-021').replace('ordered_chain_equals_full_020=True','ordered_chain_equals_full_021=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

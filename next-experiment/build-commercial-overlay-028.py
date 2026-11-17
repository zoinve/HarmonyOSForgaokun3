"""Verify the bounded diagnostic overlay against the complete build."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-027.py')))['payload']
payload=payload.replace('commercial61-native-027','commercial61-native-028').replace('ordered_chain_equals_full_027=True','ordered_chain_equals_full_028=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

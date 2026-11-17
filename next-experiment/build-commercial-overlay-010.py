"""Only own Linux harness changes over the immutable commercial 001 base."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-008.py')))['payload'].replace('commercial61-native-008','commercial61-native-010')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

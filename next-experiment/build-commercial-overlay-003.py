"""Independent commercial diagnostic overlay; keep the original 001 base intact."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-002.py')))['payload']
payload=payload.replace('commercial61-native-002','commercial61-native-003')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)

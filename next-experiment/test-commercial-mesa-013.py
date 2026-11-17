"""ELF/ISO-runtime verification of the feature-detection-compatible build."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('test-commercial-mesa-011.py')))['payload']
payload=payload.replace('commercial-mesa-011','commercial-mesa-013').replace('lab-commercial011','lab-commercial013')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60).returncode)

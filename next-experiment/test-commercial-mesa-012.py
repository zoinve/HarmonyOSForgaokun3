"""Same ELF/ISO runtime gate, applied to the independently rebuilt 012 tree."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('test-commercial-mesa-011.py')))['payload']
payload=payload.replace('commercial-mesa-011','commercial-mesa-012').replace('lab-commercial011','lab-commercial012')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60).returncode)

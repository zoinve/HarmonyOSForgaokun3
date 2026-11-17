"""Build confirmed diagnostic readbacks without altering the real copy decisions."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-033.py')))['payload']
payload=payload.replace('commercial-egl-033','commercial-egl-035').replace('commercial-gl-dispatch-033.py','commercial-readback-035.py').replace('egl-trace-033.cpp','egl-trace-035.cpp')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

"""Rebuild only the diagnostic domain correction, retaining original runtime links."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-025.py')))['payload']
# Keep the established 024 compiler/source manifest and runtime link closure.
payload=payload.replace('commercial-egl-025','commercial-egl-026').replace('commercial-egl-trace-025.py','commercial-egl-trace-026.py').replace('egl-trace-025.cpp','egl-trace-026.cpp')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

"""Build result-preserving diagnostics for our existing EGL implementation."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-028.py')))['payload']
payload=payload.replace('commercial-egl-028','commercial-egl-029').replace('commercial-egl-trace-028.py','commercial-egl-trace-029.py').replace('egl-trace-028.cpp','egl-trace-029.cpp')
assert payload.count('per_process_log_limit=152')==1
payload=payload.replace('per_process_log_limit=152','per_process_log_limit=176',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

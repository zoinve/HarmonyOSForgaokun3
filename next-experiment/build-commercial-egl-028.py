"""Build bounded post-display diagnostics against the original runtime."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-027.py')))['payload']
payload=payload.replace('commercial-egl-027','commercial-egl-028').replace('commercial-egl-trace-027.py','commercial-egl-trace-028.py').replace('egl-trace-027.cpp','egl-trace-028.cpp')
assert payload.count('per_process_log_limit=48')==1
payload=payload.replace('per_process_log_limit=48','per_process_log_limit=152',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

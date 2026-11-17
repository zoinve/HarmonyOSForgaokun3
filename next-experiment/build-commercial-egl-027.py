"""Build the per-stage quota correction, with unchanged runtime linkage."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-026.py')))['payload']
payload=payload.replace('commercial-egl-026','commercial-egl-027').replace('commercial-egl-trace-026.py','commercial-egl-trace-027.py').replace('egl-trace-026.cpp','egl-trace-027.cpp')
assert payload.count('per_process_log_limit=64')==1
payload=payload.replace('per_process_log_limit=64','per_process_log_limit=48,per_stage_log_limit=8',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

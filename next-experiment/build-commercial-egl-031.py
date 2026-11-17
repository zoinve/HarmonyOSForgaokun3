"""Build bounded real framebuffer sampling, retaining original runtime closure."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-029.py')))['payload']
payload=payload.replace('commercial-egl-029','commercial-egl-031').replace('commercial-egl-trace-029.py','commercial-egl-pixels-031.py').replace('egl-trace-029.cpp','egl-trace-031.cpp')
assert payload.count('per_process_log_limit=176')==1
payload=payload.replace('per_process_log_limit=176','per_process_log_limit=208',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

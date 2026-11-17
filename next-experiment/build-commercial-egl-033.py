"""Build read-only public GL dispatch observations, not a replacement GL frontend."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-031.py')))['payload']
payload=payload.replace('commercial-egl-031','commercial-egl-033').replace('commercial-egl-pixels-031.py','commercial-gl-dispatch-033.py').replace('egl-trace-031.cpp','egl-trace-033.cpp')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)

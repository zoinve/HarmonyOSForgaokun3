"""Same provider closure, with real DRM/GBM/display boundary diagnostics."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-005.py')))['payload']
payload = payload.replace('original-graphics-egl-005', 'original-graphics-egl-006')
payload = payload.replace('original-graphics-egl-trace-003.py', 'original-graphics-egl-trace-004.py')
compile(payload, 'original-graphics-egl-006', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

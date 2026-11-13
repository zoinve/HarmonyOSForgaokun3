"""Same Mesa closure, adding failure-only real loader diagnostics."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-006.py')))['payload']
payload = payload.replace('original-graphics-egl-006', 'original-graphics-egl-007')
payload = payload.replace('original-graphics-egl-trace-004.py', 'original-graphics-egl-trace-005.py')
compile(payload, 'original-graphics-egl-007', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

"""Same real bridge with bounded, non-saturating diagnostic records."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-004.py')))['payload']
payload = payload.replace('original-graphics-egl-004', 'original-graphics-egl-005')
payload = payload.replace('original-graphics-egl-trace-002.py', 'original-graphics-egl-trace-003.py')
compile(payload, 'original-graphics-egl-005', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

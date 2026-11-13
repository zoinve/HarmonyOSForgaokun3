"""New bridge diagnostic package; original service and SDK remain untouched."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-003.py')))['payload']
payload = payload.replace('original-graphics-egl-003', 'original-graphics-egl-004')
payload = payload.replace('original-graphics-egl-trace-001.py', 'original-graphics-egl-trace-002.py')
compile(payload, 'original-graphics-egl-004', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

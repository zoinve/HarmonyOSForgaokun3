"""Build bounded late GL observations using the retained runtime closure."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-egl-035.py')))['payload']
payload = payload.replace('commercial-egl-035', 'commercial-egl-067').replace(
    'commercial-readback-035.py', 'commercial-late-readback-067.py').replace(
    'egl-trace-035.cpp', 'egl-trace-067.cpp')
payload = payload.replace('per_process_log_limit=208', 'per_process_log_limit=262')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(
        ['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
        text=True, timeout=180).returncode)

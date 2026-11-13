"""Build a fresh provider with real Commit-result logging, not service changes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-provider-004.py')))['payload']
payload = payload.replace('original-graphics-provider-004', 'original-graphics-provider-005')
payload = payload.replace('original-composer-trace-002.py', 'original-composer-trace-003.py')
compile(payload, 'original-content-provider-005', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)

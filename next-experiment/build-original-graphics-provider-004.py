"""Preserve failed build003; use macro-safe reversible tracing in a fresh build."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-provider-003.py')))['payload']
payload = payload.replace('original-graphics-provider-003', 'original-graphics-provider-004')
payload = payload.replace('original-composer-trace-001.py', 'original-composer-trace-002.py')
compile(payload, 'original-graphics-provider-004', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                            text=True, timeout=240)
    raise SystemExit(result.returncode)

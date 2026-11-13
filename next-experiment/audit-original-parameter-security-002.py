"""Resolve the module's actual original filename; preserve failed audit001 evidence."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-security-001.py')))['payload']
payload = payload.replace('original-parameter-security-001', 'original-parameter-security-002')
payload = payload.replace('/autorun/init_security.z.so', '/autorun/libinit_security.z.so')
compile(payload, 'original-parameter-security-002', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

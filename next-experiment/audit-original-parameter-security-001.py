"""Read-only original security-module evidence; never change parameter permissions."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
payload = payload.replace('original-parameter-loader-001', 'original-parameter-security-001')
assert "work/'init'" in payload
payload = payload.replace("work/'init'", "work/'init_security.z.so'")
assert '/system/bin/init' in payload
payload = payload.replace('/system/bin/init', '/system/lib64/init/autorun/init_security.z.so')
compile(payload, 'original-parameter-security-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

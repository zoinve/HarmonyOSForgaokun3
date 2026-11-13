"""Inspect genuine directory enumeration code; never execute the target ELF."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-config-layer-001.py')))['payload']
payload = payload.replace('original-config-layer-001', 'original-directory-utils-001')
payload = payload.replace('libconfigpolicy_util.z.so', 'libutils.z.so')
compile(payload, 'original-directory-utils-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

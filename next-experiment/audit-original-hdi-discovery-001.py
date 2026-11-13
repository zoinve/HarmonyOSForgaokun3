"""Read-only original HDI discovery symbols; never execute or patch the ELF."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-workspace-001.py')))['payload']
payload = payload.replace('original-parameter-workspace-001', 'original-hdi-discovery-001')
payload = payload.replace('libbegetutil.z.so', 'libhdi.z.so')
compile(payload, 'original-hdi-discovery-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

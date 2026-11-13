"""Inspect the original configuration library without executing target code."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-workspace-001.py')))['payload']
payload = payload.replace('original-parameter-workspace-001', 'original-config-layer-001')
payload = payload.replace('libbegetutil.z.so', 'libconfigpolicy_util.z.so')
compile(payload, 'original-config-layer-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

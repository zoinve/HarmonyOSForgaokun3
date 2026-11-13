"""Read-only genuine parameter-workspace implementation, without changing security rules."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
payload = payload.replace('original-parameter-loader-001', 'original-parameter-workspace-001')
payload = payload.replace("work/'init'", "work/'libbegetutil.z.so'")
payload = payload.replace('/system/bin/init', '/system/lib64/chipset-sdk-sp/libbegetutil.z.so')
compile(payload, 'original-parameter-workspace-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

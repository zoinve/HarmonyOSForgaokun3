"""Clone-only forensic recovery for the fresh disposable 089 userdata."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('recover-original-audit-copy-088.py')))['payload']
payload = payload.replace('original-init-qemu-088', 'original-init-qemu-089')
payload = payload.replace('original-audit-copy-088', 'original-audit-copy-089')
payload = payload.replace('graphics-audit-088.log', 'graphics-audit-089.log')
compile(payload, 'recover-audit-copy-089', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

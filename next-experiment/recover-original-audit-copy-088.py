"""Read a recovery clone of new disposable guest data, never the source images."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('recover-original-audit-copy-087.py')))['payload']
payload = payload.replace('original-init-qemu-087', 'original-init-qemu-088')
payload = payload.replace('original-audit-copy-087', 'original-audit-copy-088')
payload = payload.replace('graphics-audit-087.log', 'graphics-audit-088.log')
compile(payload, 'recover-audit-copy-088', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

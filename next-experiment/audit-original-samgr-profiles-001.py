"""Inspect original SAMgr profile loading, preserving original image bytes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
payload = payload.replace('original-parameter-loader-001', 'original-samgr-profiles-001')
payload = payload.replace("work/'init'", "work/'samgr'")
payload = payload.replace('/system/bin/init', '/system/bin/samgr')
payload = payload.replace('original_init_elf_', 'original_samgr_elf_')
compile(payload, 'original-samgr-profile-audit-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

"""Read-only extraction/symbol audit of the genuine original profile parser."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
payload = payload.replace('original-parameter-loader-001', 'original-sa-parser-001')
payload = payload.replace("work/'init'", "work/'libsamgr_common.z.so'")
payload = payload.replace('/system/bin/init', '/system/lib64/platformsdk/libsamgr_common.z.so')
payload = payload.replace('original_init_elf_', 'original_sa_parser_elf_')
compile(payload, 'original-sa-parser-audit-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

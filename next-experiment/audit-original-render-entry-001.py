"""Read the authentic render_service entry/dependencies; never run its ELF."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-parameter-loader-001.py')))['payload']
assert 'original-parameter-loader-001' in payload
payload = payload.replace('original-parameter-loader-001', 'original-render-entry-001')
payload = payload.replace("work/'init'", "work/'render_service'")
payload = payload.replace('/system/bin/init', '/system/bin/render_service')
payload = payload.replace("['llvm-nm-19','-DC',str(elf)]", "['llvm-objdump-19','-dC',str(elf)]")
payload = payload.replace('original_init_elf_path=', 'render_entry_elf_path=').replace(
    'original_init_elf_sha256=', 'render_entry_elf_sha256=')
compile(payload, 'original-render-entry-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

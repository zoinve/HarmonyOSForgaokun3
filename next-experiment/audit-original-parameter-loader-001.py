"""Read-only original init symbols and loader dependencies for real parameter DAC diagnosis."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-render-fault-054.py')))['payload']
payload = payload.replace('original-render-fault-054', 'original-parameter-loader-001')
payload = payload.replace("work/'librender_service.z.so'", "work/'init'")
payload = payload.replace('/system/lib64/librender_service.z.so', '/system/bin/init')
payload = payload.replace("['llvm-objdump-19','-dC','--start-address=0x40f25c','--stop-address=0x40f520',str(elf)]",
                          "['llvm-nm-19','-DC',str(elf)], ['llvm-readelf-19','-dW',str(elf)]")
payload = payload.replace("assert b'2ceb723e313c80c3605ecd369c0b8cb6' in (out/'0.stdout.txt').read_bytes()", '')
payload = payload.replace('rs_elf_path=', 'original_init_elf_path=').replace('rs_elf_sha256=', 'original_init_elf_sha256=')
compile(payload, 'original-parameter-loader-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

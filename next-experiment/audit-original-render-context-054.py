"""Read-only dependency symbols for the original RenderContext implementation."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-render-fault-054.py')))['payload']
payload = payload.replace('original-render-fault-054', 'original-render-context-054')
payload = payload.replace('librender_service.z.so', 'librender_service_base.z.so')
payload = payload.replace("['llvm-objdump-19','-dC','--start-address=0x40f25c','--stop-address=0x40f520',str(elf)]",
                          "['llvm-nm-19','-DC',str(elf)]")
payload = payload.replace("assert b'2ceb723e313c80c3605ecd369c0b8cb6' in (out/'0.stdout.txt').read_bytes()",
                          "assert b'OHOS::Rosen::RenderContext::Create()' in (out/'1.stdout.txt').read_bytes()")
compile(payload, 'original-render-context-audit-054', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

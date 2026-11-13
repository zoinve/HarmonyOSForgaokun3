"""Read-only original BMS symbols; identify directory setup before any adaptation."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-render-context-054.py')))['payload']
payload = payload.replace('original-render-context-054', 'original-bms-paths-001')
payload = payload.replace('librender_service_base.z.so', 'libbms.z.so')
payload = payload.replace("assert b'OHOS::Rosen::RenderContext::Create()' in (out/'1.stdout.txt').read_bytes()",
                          "assert b'Bundle' in (out/'1.stdout.txt').read_bytes()")
assert "'debugfs','-R','dump /system/lib64/libbms.z.so '" in payload
assert 'original-bms-paths-001' in payload
compile(payload, 'original-bms-paths-audit-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

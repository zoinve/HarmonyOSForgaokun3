"""Read-only symbols of the genuine original graphics composer client."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('audit-original-render-context-054.py')))['payload']
payload = payload.replace('original-render-context-054', 'original-composer-client-001')
payload = payload.replace('librender_service_base.z.so', 'libcomposer.z.so')
payload = payload.replace("b'OHOS::Rosen::RenderContext::Create()'", "b'HdiDevice::GetInstance'")
compile(payload, 'original-composer-client-audit-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

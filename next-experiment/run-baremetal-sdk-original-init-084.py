"""Only add bounded notification observation inside the isolated original guest."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-083.py')))['payload']
for old, new in [('original-init-qemu-083','original-init-qemu-084'),
                 ('harmony-sdk-qemu083-','harmony-sdk-qemu084-'),
                 ('original-init-083/result.json','original-init-084/result.json'),
                 ('GRAPHICS083_','GRAPHICS084_'), ('ORIGINAL_INIT083_','ORIGINAL_INIT084_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
compile(payload, 'original-profile-events-084-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'], input=payload,
                                   text=True, timeout=660).returncode)

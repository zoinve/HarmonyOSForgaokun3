"""Bounded virtual resource/observability trial; original services unchanged."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-063.py')))['payload']
for old, new in [('original-init-qemu-063', 'original-init-qemu-064'),
                 ('harmony-sdk-qemu063-', 'harmony-sdk-qemu064-'),
                 ('original-init-063/result.json', 'original-init-064/result.json'),
                 ('GRAPHICS063_', 'GRAPHICS064_'), ('ORIGINAL_INIT063_', 'ORIGINAL_INIT064_'),
                 ('original-graphics-egl-008', 'original-graphics-egl-009'),
                 ("'-smp','2','-m','2048'", "'-smp','8','-m','4096'")]:
    assert old in payload
    payload = payload.replace(old, new)
compile(payload, 'original-graphics-064-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)

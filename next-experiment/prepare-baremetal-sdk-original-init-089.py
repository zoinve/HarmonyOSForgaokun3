"""Preserve the original system image's nodev flag on its canonical bind mount."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-088.py')))
source = parent['source'].replace('ORIGINAL_INIT088_', 'ORIGINAL_INIT089_').replace('GRAPHICS088_', 'GRAPHICS089_')
source = source.replace('graphics_profile_events_088', 'graphics_profile_events_089')
source = source.replace('graphics_audit_copy_088', 'graphics_audit_copy_089')
source = source.replace('graphics-audit-088.log', 'graphics-audit-089.log')
old = 'mount(NULL, "/system", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY, NULL)'
assert source.count(old) == 1
source = source.replace(old, 'mount(NULL, "/system", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV, NULL)')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-088', 'baremetal-sdk-original-init-089')
compile(payload, 'original-system-bind-089-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)

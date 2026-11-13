"""Resolve the pinned cpio DRM symlink; preserve failed build001 unchanged."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-provider-001.py')))['payload']
payload = payload.replace('original-graphics-provider-001', 'original-graphics-provider-002')
anchor = "drm=entries['system/lib64/lab-softpipe-167/libdrm.so.2'][1]"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """mode,drm_link=entries['system/lib64/lab-softpipe-167/libdrm.so.2']
assert mode&0o170000==0o120000 and drm_link==b'libdrm.so.2.124.0'
drm=entries['system/lib64/lab-softpipe-167/libdrm.so.2.124.0'][1]
assert drm[:4]==b'\\x7fELF'""")
compile(payload, 'original-graphics-provider-002', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                            text=True, timeout=240)
    raise SystemExit(result.returncode)

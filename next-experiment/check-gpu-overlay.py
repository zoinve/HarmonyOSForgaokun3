"""Check GPU RAM overlay boundaries without booting or changing disk images."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = (base / 'payload-881/init.c').read_text()
transform = runpy.run_path(str(base / 'gpu-overlay.py'))['gpu_overlay']
updated = transform(source)
assert updated.count('GPU883_RAM_OVERLAY') == 1
assert '"/newroot/system/lib64/libEGL.so"' not in updated
assert '"/newroot/system/lib64/libEGL_mesa.so"' in updated
assert '"/newroot/system/lib64/libgallium-25.0.1.so"' in updated
assert updated.count('MS_BIND|MS_REMOUNT|MS_RDONLY') == source.count('MS_BIND|MS_REMOUNT|MS_RDONLY') + 3
assert updated.count('MS_RDONLY|MS_NODEV') == source.count('MS_RDONLY|MS_NODEV')
assert updated.count('persist.sys.graphic.blurEnabled') == source.count('persist.sys.graphic.blurEnabled')
assert ':/system/lib64/lab-softpipe-167"' in updated
try:
    transform('no valid boot anchor')
except AssertionError:
    pass
else:
    raise AssertionError('unknown boot payload must not be patched')
print('PASS: RAM-only read-only GPU overlays; original EGL frontend/disk mounts preserved')

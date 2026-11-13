from pathlib import Path
import runpy
base = Path(__file__).resolve().parent
transform = runpy.run_path(str(base/'gpu-allocator-overlay.py'))['allocator_overlay']
source = (base/'payload-906/init.c').read_text()
updated = transform(source)
start = updated.index('    /* GPU907 allocator RAM-only overlay. */')
end = updated.index('    /* GPU907 allocator overlay end. */', start) + len('    /* GPU907 allocator overlay end. */\n')
assert updated[:start] + updated[end:] == source
change = updated[start:end]
assert '/gpu883-libs/gpu905-buffer-vdi.so' in change
assert '/newroot/vendor/lib64/libdisplay_buffer_vdi_impl.z.so' in change
assert 'MS_BIND|MS_REMOUNT|MS_RDONLY' in change
assert 'chmod' not in change and 'setuid' not in change
print('PASS: only readonly RAM allocator bind; original config and identities unchanged')

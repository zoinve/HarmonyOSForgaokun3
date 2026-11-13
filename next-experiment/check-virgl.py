"""Configuration-only check: headless GL must preserve native KVM/disk guards."""
from pathlib import Path
import sys

path = Path(__file__).with_name('run.py').resolve()
number = next(n for n in range(9883, 99999) if not path.with_name(f'run-{n}').exists())
sys.argv = [str(path), str(number), '--virgl', '--relative-mouse']
ns = {'__file__': str(path)}
text = path.read_text()
exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")], str(path), 'exec'), ns)
command = ns['c']['command']
assert 'virtio-gpu-gl-pci,xres=1920,yres=1080' in command
assert command[command.index('-display') + 1] == 'egl-headless,rendernode=/dev/dri/renderD128'
assert command[command.index('-accel') + 1] == 'kvm'
assert ns['c'].get('qmp_screenshots_enabled') is False
assert 'QEMU_MODULE_DIR' in ns['source']
assert "env=qemu_env" in ns['source']
assert 'physical_screen_viewer_pid' not in ns['source']
assert 'protected_userdata_original_unchanged' in ns['source']
assert 'readonly_inputs_unchanged' in ns['source']
print('PASS: isolated headless VirGL, native KVM and original disk guards')

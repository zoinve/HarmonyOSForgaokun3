"""A reduced framebuffer is opt-in and must not enable physical viewing."""
from pathlib import Path
import sys

path = Path(__file__).with_name('run.py').resolve()
number = next(n for n in range(9878, 99999) if not path.with_name(f'run-{n}').exists())
text = path.read_text()
for extra, expected in [([], '1920,yres=1080'), (['--diagnostic-resolution', '960x540'], '960,yres=540')]:
    sys.argv = [str(path), str(number), *extra]
    scope = {'__file__': str(path)}
    exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")], str(path), 'exec'), scope)
    assert 'virtio-gpu-pci,xres=' + expected in scope['c']['command']
    assert 'physical_screen_viewer_pid' not in scope['source']
print('PASS: default 1080p preserved; explicit reduced diagnostic framebuffer remains headless')

"""Check generated boot input configuration without starting a guest."""
from pathlib import Path
import sys

path = Path(__file__).with_name('run.py').resolve()
number = next(n for n in range(9872, 100000) if not (path.parent / f'run-{n}').exists())
sys.argv = [str(path), str(number), '--on-screen', '--quiet-trace', '--relative-mouse']
text = path.read_text()
scope = {'__file__': str(path)}
exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")], str(path), 'exec'), scope)
command = scope['c']['command']
assert command.count('usb-mouse') == 1
assert 'usb-tablet' not in command
assert 'usb-kbd' in command
assert 'virtio-gpu-pci,xres=1920,yres=1080' in command
print('PASS: relative USB mouse, keyboard and native 1080p; runner compiles')

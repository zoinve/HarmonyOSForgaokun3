"""Long headless observations must not enable a physical viewer."""
from pathlib import Path
import sys

path = Path(__file__).with_name('run.py').resolve()
number = next(n for n in range(9877, 99999) if not path.with_name(f'run-{n}').exists())
sys.argv = [str(path), str(number), '--duration', '1200', '--relative-mouse']
text = path.read_text()
scope = {'__file__': str(path)}
exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")], str(path), 'exec'), scope)
assert 'elapsed>=1200' in scope['source']
assert 'wall_limit_seconds=1200' in scope['source']
assert 'physical_screen_viewer_pid' not in scope['source']
assert scope['c']['command'][scope['c']['command'].index('-display') + 1] == 'none'
print('PASS: bounded 1200-second headless observation without a physical viewer')

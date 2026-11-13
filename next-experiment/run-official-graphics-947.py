"""Fresh 947 uses the guarded runner, normal official init and EGL diagnostics."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'run-official-graphics-941.py').read_text()
assert source.count('941') == 5
source = source.replace('941', '947')
exec(compile(source, 'run-official-graphics-947-generated', 'exec'))

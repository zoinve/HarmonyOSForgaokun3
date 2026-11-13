"""Fresh 944 uses the verified 941 runner with only new experiment paths."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'run-official-graphics-941.py').read_text()
assert source.count('941') == 5
source = source.replace('941', '944')
compile(source, 'run-official-graphics-944-generated', 'exec')
exec(compile(source, 'run-official-graphics-944-generated', 'exec'))

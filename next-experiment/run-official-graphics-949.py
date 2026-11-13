"""Bounded native-KVM diagnostic run; never overwrite a completed experiment."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'run-official-graphics-941.py').read_text()
assert source.count('941') == 5
source = source.replace('941', '949')
exec(compile(source, 'run-graphics-949-generated', 'exec'))

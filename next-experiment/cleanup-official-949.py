"""Preserve and verify 949 evidence before removing only its writable userdata."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'cleanup-official-944.py').read_text()
assert source.count('944') >= 4
exec(compile(source.replace('944', '949'), 'cleanup-949-generated', 'exec'))

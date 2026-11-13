"""Exact guarded cleanup, retaining the completed 947 crash/log evidence."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'cleanup-official-944.py').read_text()
assert source.count('944') >= 4
source = source.replace('944', '947')
exec(compile(source, 'cleanup-947-generated', 'exec'))

"""Exact guarded cleanup after all 961 evidence is preserved."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'cleanup-official-959.py').read_text().replace('959','961')
exec(compile(source,'cleanup-961-generated','exec'))

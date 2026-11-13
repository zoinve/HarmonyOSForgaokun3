"""Preserve completed display run 961, without userdata writes."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'preserve-evidence-959.py').read_text().replace('959','961')
exec(compile(source,'preserve-961-generated','exec'))

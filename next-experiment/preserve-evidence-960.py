"""Preserve completed 960 evidence without modifying its userdata."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'preserve-evidence-959.py').read_text().replace('959','960')
exec(compile(source,'preserve-960-generated','exec'))

"""Exact guarded cleanup of completed 960 after evidence preservation."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'cleanup-official-959.py').read_text().replace('959','960')
exec(compile(source,'cleanup-960-generated','exec'))

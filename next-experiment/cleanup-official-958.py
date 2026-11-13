"""Exact guarded 958 cleanup; preserve all ten independently verified logs."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'cleanup-official-951.py').read_text()
assert source.count('951')==5
source=source.replace('951','958').replace('len(manifest)==8','len(manifest)==10')
exec(compile(source,'cleanup-958','exec'))

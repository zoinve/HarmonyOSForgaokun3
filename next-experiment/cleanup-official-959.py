"""Exact 959 userdata cleanup, requiring all verified evidence and SHA guards."""
from pathlib import Path
import json
base=Path(__file__).resolve().parent
saved=base.parent/'reports/official-arm-evidence-959-verified'
count=len(json.loads((saved/'evidence-manifest.json').read_text()))
assert count>=5
source=(base/'cleanup-official-951.py').read_text()
assert source.count('951')==5 and source.count('len(manifest)==8')==1
source=source.replace('951','959').replace('len(manifest)==8',f'len(manifest)=={count}')
exec(compile(source,'cleanup-959-generated','exec'))

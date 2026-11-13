"""Fresh trial of the same official account CLI with corrected root discovery."""
from pathlib import Path
base=Path(__file__).resolve().parent
source=(base/'run-official-account-959.py').read_text().replace('959','960')
anchor="reports/userdata-cleanup-official-958.json"
assert source.count(anchor)==1
source=source.replace(anchor,'reports/userdata-cleanup-official-959.json')
exec(compile(source,'run-account-960-generated','exec'))

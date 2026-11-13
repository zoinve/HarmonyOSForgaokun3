"""Run the real snapshot-safety harness against the render-sandbox diagnostic candidate."""
from pathlib import Path

base=Path(__file__).resolve().parent
source=(base/'test-baremetal-diagnostic-log-009.py').read_text()
anchor="'native-identity-009'))"
assert source.count(anchor)==1
source=source.replace(anchor,"'native-identity-009','mesa-010'))")
exec(compile(source,'snapshot-010-harness','exec'))

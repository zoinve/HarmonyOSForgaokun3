"""Run real snapshot harness against 007 while preserving prior candidates."""
from pathlib import Path
import sys

base = Path(__file__).resolve().parent
source = (base / 'test-baremetal-diagnostic-log.py').read_text()
anchor = "contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-deadline-004.py'))['build_source'](contents)"
assert source.count(anchor) == 1
extra = ''.join("\n                contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-" + version + ".py'))['build_source'](contents)" for version in ('display-005', 'observation-006', 'ucsi-007'))
source = source.replace(anchor, anchor + extra)
sys.argv.append('--candidate-004')
exec(compile(source, 'snapshot-007-harness', 'exec'))

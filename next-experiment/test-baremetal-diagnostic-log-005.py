"""Reuse the real snapshot harness against generated 005 without editing old tests."""
from pathlib import Path
import sys

base = Path(__file__).resolve().parent
source = (base / 'test-baremetal-diagnostic-log.py').read_text()
anchor = "contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-deadline-004.py'))['build_source'](contents)"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + "\n                contents = runpy.run_path(str(BASE / 'baremetal-diagnostic-display-005.py'))['build_source'](contents)")
sys.argv.append('--candidate-004')
exec(compile(source, 'snapshot-005-harness', 'exec'))

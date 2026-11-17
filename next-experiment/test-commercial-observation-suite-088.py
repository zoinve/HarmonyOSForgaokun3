"""Retain previous regression coverage and add canonical config-view checks."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base / 'test-commercial-observation-suite-087.py'))['source']
source = source.replace('reports/commercial61-native-087/test-results.json', 'reports/commercial61-native-088/test-results.json')
anchor = "'test-commercial-dock-literals-086.py')"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "'test-commercial-dock-literals-086.py', 'test-commercial-config-sandbox-088.py', 'test-commercial-config-view-analysis-088.py')", 1)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

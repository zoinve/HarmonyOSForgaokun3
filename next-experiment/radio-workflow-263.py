"""Reuse the direct single-boot workflow for radio262; no storage suites."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent


if __name__ == '__main__':
    source = (BASE / 'settings-workflow-254.py').read_text()
    source = source.replace('253', '262').replace('235', '253')
    source = source.replace('native Settings real-time budget 262', 'native QCA Bluetooth and device profile 262')
    rows = json.loads((BASE.parent / 'reports/commercial61-native-262/result.json').read_text())['artifacts']
    digest = next(row['sha256'] for row in rows if row['name'] == 'bootstrap-runtime087')
    original = 'fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'
    assert source.count(original) == 1
    source = source.replace(original, digest)
    exec(compile(source, 'radio-workflow-263.generated.py', 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / 'radio-workflow-263.generated.py')})

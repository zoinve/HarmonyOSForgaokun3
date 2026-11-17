"""Single guarded471 experiment; retain desktop173 and archive458 entry."""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'settings-workflow-254.py').read_text().replace('253', '471').replace('235', '458')
    rows = json.loads((BASE.parent / 'reports/commercial61-native-471/result.json').read_text())['artifacts']
    digest = next(row['sha256'] for row in rows if row['name'] == 'bootstrap-runtime087')
    source = source.replace('fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122', digest)
    source = source.replace('native Settings real-time budget 471', 'native cpufreq dependency verification 471')
    exec(compile(source, 'cpufreq-workflow-474.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'cpufreq-workflow-474.generated.py')))

from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'settings-workflow-254.py').read_text()
    source = source.replace('253', '294').replace('235', '285')
    rows = json.loads((BASE.parent / 'reports/commercial61-native-294/result.json').read_text())['artifacts']
    digest = next(row['sha256'] for row in rows if row['name'] == 'bootstrap-runtime087')
    source = source.replace('fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122', digest)
    source = source.replace('native Settings real-time budget 294', 'native Bluetooth entry diagnostics 294')
    exec(compile(source, 'radio-workflow-295.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'radio-workflow-295.generated.py')))

from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'collect-settings-253-256.py').read_text()
    source = source.replace('commercial61-native-253', 'commercial61-native-262')
    source = source.replace('commercial-return-audit-253', 'commercial-return-audit-262')
    source = source.replace('256', '265')
    marker = '        prior = json.loads('
    assert source.count(marker) == 1
    insertion = '''        previous = json.loads((ROOT / 'reports/commercial61-native-253/runtime-evidence/retrieval-manifest.json').read_text())['run']
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
'''
    source = source.replace(marker, insertion + marker, 1)
    exec(compile(source, 'collect-radio-262-265.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-262-265.generated.py')))

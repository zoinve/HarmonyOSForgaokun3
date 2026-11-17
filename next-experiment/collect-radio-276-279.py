from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'collect-settings-253-256.py').read_text()
    source = source.replace('commercial61-native-253', 'commercial61-native-276')
    source = source.replace('commercial-return-audit-253', 'commercial-return-audit-276')
    source = source.replace('256', '279')
    marker = '        prior = json.loads('
    insertion = '''        for candidate in ['253', '262', '266']:
            previous = json.loads((ROOT / ('reports/commercial61-native-' + candidate + '/runtime-evidence/retrieval-manifest.json')).read_text())['run']
            source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
'''
    assert source.count(marker) == 1
    source = source.replace(marker, insertion + marker, 1)
    exec(compile(source, 'collect-radio-276-279.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-276-279.generated.py')))

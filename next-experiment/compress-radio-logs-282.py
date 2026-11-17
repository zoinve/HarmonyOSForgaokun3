from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'compress-historical-logs-226.py').read_text()
    source = source.replace('historical-log-compression-226.json', 'radio-log-compression-282.json')
    old = '    for raw in sorted((ROOT / ' + repr('reports') + ').glob(' + repr('*/runtime-evidence/raw') + ')):'
    new = '''    for raw in [ROOT / ('reports/commercial61-native-' + candidate + '/runtime-evidence/raw')
                for candidate in ['253', '262', '266']]:'''
    assert source.count(old) == 1
    source = source.replace(old, new, 1)
    exec(compile(source, 'compress-radio-logs-282.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'compress-radio-logs-282.generated.py')))

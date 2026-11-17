from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'collect-radio-262-265.py').read_text()
    source = source.replace('262', '266').replace('265', '269')
    marker = '    exec(compile(source,'
    extra = '''    anchor = '        prior = json.loads('
    insertion = ''' + repr('''        previous262 = json.loads((ROOT / 'reports/commercial61-native-262/runtime-evidence/retrieval-manifest.json').read_text())['run']
        source = source.replace(anchor, anchor + repr(previous262) + ', ', 1)
''') + '''
    source = source.replace(marker, insertion + marker, 1)
'''
    assert source.count(marker) == 1
    source = source.replace(marker, extra + marker, 1)
    exec(compile(source, 'collect-radio-266-269.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'collect-radio-266-269.generated.py')))

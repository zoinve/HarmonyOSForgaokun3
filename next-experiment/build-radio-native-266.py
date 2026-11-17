from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'build-radio-native-262.py').read_text()
    source = source[:source.index('    report = BASE.parent')]
    source = source.replace('commercial61-native-262', 'commercial61-native-266')
    marker = '    env = dict(MODULE,'
    insertion = '''    anchor = '        stage = Path(tmp)'
    extra = ''' + repr('''        stage = Path(tmp)
        for header in ['persistent-data-166.h', 'persistent-data-172.h', 'persistent-unmount-plan-201.h', 'native-live-debug-159.h']:
            os.link(parent / header, stage / header)''') + '''
    assert source.count(anchor) == 1
    source = source.replace(anchor, extra, 1)
'''
    assert source.count(marker) == 1
    source = source.replace(marker, insertion + marker, 1)
    exec(compile(source, 'build-radio-native-266.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-radio-native-266.generated.py')))

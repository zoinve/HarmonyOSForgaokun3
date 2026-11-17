from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-account-063.py').read_text()
source = source.replace('reports/commercial61-native-063', 'reports/commercial61-native-066').replace('COMMERCIAL063_OUTER_STREAM', 'COMMERCIAL066_OUTER_STREAM')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

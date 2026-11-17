from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-layout-065.py').read_text().replace('reports/commercial61-native-065', 'reports/commercial61-native-066')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

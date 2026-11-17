from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-endpoints-044.py').read_text()
source = source.replace('reports/commercial61-native-044', 'reports/commercial61-native-045')
source = source.replace('COMMERCIAL044_OUTER_', 'COMMERCIAL045_OUTER_')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

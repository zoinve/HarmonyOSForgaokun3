from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-full-frame-068.py').read_text().replace(
    'reports/commercial61-native-068', 'reports/commercial61-native-073').replace(
    'COMMERCIAL068_FULL_EXPORT', 'COMMERCIAL073_FULL_EXPORT')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

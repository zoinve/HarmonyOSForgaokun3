from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-allocator-073.py').read_text().replace(
    'reports/commercial61-native-073', 'reports/commercial61-native-074')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

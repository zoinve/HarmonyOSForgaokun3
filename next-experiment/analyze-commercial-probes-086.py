from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'analyze-commercial-probes-085.py').read_text()
for old, new in ((r'(?P<mode>\w+)085', r'(?P<mode>\w+)086'),
                 (r'(?P=mode)085', r'(?P=mode)086'),
                 ('commercial61-native-085', 'commercial61-native-086')):
    assert old in source
    source = source.replace(old, new)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

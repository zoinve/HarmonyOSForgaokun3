"""Reuse kernel/WPA analysis, changing phase labels only; retain original084 markers."""
from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'analyze-commercial-network-084.py').read_text()
for old, new in ((r'(?P<mode>\w+)084', r'(?P<mode>\w+)085'),
                 (r'(?P=mode)084', r'(?P=mode)085'),
                 ('commercial61-native-084', 'commercial61-native-085'),
                 ('COMMERCIAL084', 'COMMERCIAL085')):
    assert old in source
    source = source.replace(old, new)

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

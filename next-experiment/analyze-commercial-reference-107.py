from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'analyze-commercial-reference-099.py').read_text().replace('commercial61-native-099', 'commercial61-native-107')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

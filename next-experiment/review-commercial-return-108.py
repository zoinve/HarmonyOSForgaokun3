from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'review-commercial-return-107.py').read_text().replace('commercial61-native-107', 'commercial61-native-108')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

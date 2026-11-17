"""Record OCR/pixel differences and original TEE failures for completed 099."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'review-commercial-return-095.py').read_text().replace('commercial61-native-095', 'commercial61-native-099')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

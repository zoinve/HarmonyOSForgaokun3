"""Apply the existing immutable baseline readers to native driver run 133."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'analyze-commercial-130.py').read_text().replace('130', '133')
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

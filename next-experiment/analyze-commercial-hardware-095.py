"""Preserve the original early093/native091 result labels in candidate 095."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'analyze-commercial-hardware-094.py').read_text().replace('commercial61-native-094', 'commercial61-native-095')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

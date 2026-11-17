"""Same original-service correlation rules applied to new085 evidence only."""
from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'analyze-commercial-native-netmanager-084.py').read_text().replace('commercial61-native-084', 'commercial61-native-085')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

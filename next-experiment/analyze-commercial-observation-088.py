"""Keep inherited core 087 and helper 086 labels while analyzing new entry 088."""
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base / 'analyze-commercial-observation-087.py'))


def source088(kind):
    return previous['source087'](kind).replace('commercial61-native-087', 'commercial61-native-088')


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in previous['SCRIPTS']
    exec(compile(source088(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

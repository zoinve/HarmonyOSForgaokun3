"""Use established raw-label-aware observations on unique entry 090."""
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base / 'analyze-commercial-observation-087.py'))
SCRIPTS = previous['SCRIPTS']


def source090(kind):
    return previous['source087'](kind).replace('commercial61-native-087', 'commercial61-native-090')


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in SCRIPTS
    exec(compile(source090(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

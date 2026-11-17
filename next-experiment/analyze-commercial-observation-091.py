"""Established observations on 091, retaining exact inherited runtime labels."""
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base/'analyze-commercial-observation-087.py'))
SCRIPTS = previous['SCRIPTS']


def source091(kind):
    return previous['source087'](kind).replace('commercial61-native-087', 'commercial61-native-091')


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in SCRIPTS
    exec(compile(source091(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

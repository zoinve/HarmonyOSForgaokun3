"""Analyze unique 089 evidence without rewriting inherited historical results."""
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base / 'analyze-commercial-observation-088.py'))


def source089(kind):
    return previous['source088'](kind).replace('commercial61-native-088', 'commercial61-native-089')


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in previous['previous']['SCRIPTS']
    exec(compile(source089(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

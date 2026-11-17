"""Reuse original observations, preserving inherited diagnostic labels."""
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base/'analyze-commercial-observation-087.py'))
SCRIPTS = previous['SCRIPTS']


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in SCRIPTS
    source = previous['source087'](sys.argv[1]).replace('commercial61-native-087', 'commercial61-native-092')
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

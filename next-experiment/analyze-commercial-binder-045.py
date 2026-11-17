"""The 044 observer/userland is byte-identical; analyze only the new run."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-binder-044.py')))['source']
source = source.replace('reports/commercial61-native-044', 'reports/commercial61-native-045')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

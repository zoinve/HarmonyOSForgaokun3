"""Reuse hash checks and unchanged inner streams; identify associated tokenless RPC."""
from pathlib import Path

source = Path(__file__).with_name('analyze-commercial-binder-043.py').read_text()
source = source.replace('reports/commercial61-native-043', 'reports/commercial61-native-044')
source = source.replace("'IPC043 phase='", "'IPC044 phase='").replace("'IPC043 '", "'IPC044 '")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

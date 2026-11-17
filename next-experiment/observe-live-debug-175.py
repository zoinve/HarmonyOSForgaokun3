"""Use the existing authenticated read-only channel during the single USB boot."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'observe-live-debug-161.py').read_text()
    source = source.replace('commercial61-native-161', 'commercial61-native-175-compile-fix-1')
    source = source.replace('harmony-native-161', 'harmony-native-175')
    exec(compile(source, 'observe-live-debug-175.generated.py', 'exec'),
         {'__name__':'__main__', '__file__':str(BASE / 'observe-live-debug-175.generated.py')})

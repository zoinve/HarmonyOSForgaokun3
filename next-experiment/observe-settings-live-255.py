"""Observe the253 Settings test through the existing pinned read-only channel."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'observe-live-debug-236.py').read_text()
    source = source.replace('commercial61-native-235', 'commercial61-native-253')
    source = source.replace('harmony-native-235', 'harmony-native-253')
    source = source.replace('observe-live-debug-236.generated.py', 'observe-settings-live-255.generated.py')
    exec(compile(source, str(__file__), 'exec'), {'__name__': '__main__', '__file__': str(__file__)})

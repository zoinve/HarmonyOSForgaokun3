"""Analyze the independent capture-first log using the verified 104 parser."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE/'analyze-server-stack-104.py').read_text().replace(
    'commercial61-native-104', 'commercial61-native-105').replace(
    'commercial-server-stack104.log', 'commercial-server-stack105.log').replace('SERVER104', 'SERVER105')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})

"""Reuse420 accounting on the newly retrieved438 run; never requests capture."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'analyze-audio-425.py').read_text()
    source = source.replace('commercial61-native-420', 'commercial61-native-438')
    source = source.replace('audio-analysis-425.json', 'audio-analysis-446.json')
    exec(compile(source, 'analyze-audio-446.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'analyze-audio-446.generated.py')))

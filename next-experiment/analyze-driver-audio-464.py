"""Analyze458 audio/touch evidence after retrieval; do not request recording."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'analyze-audio-446.py').read_text()
    source = source.replace('commercial61-native-438', 'commercial61-native-458')
    source = source.replace('audio-analysis-446.json', 'audio-analysis-464.json')
    exec(compile(source, 'analyze-driver-audio-464.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'analyze-driver-audio-464.generated.py')))

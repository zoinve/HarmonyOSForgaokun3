"""Analyze458 original service/HCI evidence after retrieval, not user acceptance."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    source = (BASE / 'analyze-bluetooth-445.py').read_text()
    source = source.replace('commercial61-native-438', 'commercial61-native-458')
    source = source.replace('bluetooth-analysis-445.json', 'bluetooth-analysis-465.json')
    exec(compile(source, 'analyze-driver-bluetooth-465.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'analyze-driver-bluetooth-465.generated.py')))

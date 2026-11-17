"""Analyze already-retrieved420 evidence; never starts or changes a scan."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
if __name__=='__main__':
    source=(BASE/'analyze-bluetooth-346.py').read_text()
    source=source.replace('commercial61-native-341','commercial61-native-420')
    source=source.replace('bluetooth-analysis-346.json','bluetooth-analysis-431.json')
    exec(compile(source,'analyze-bluetooth-431.generated.py','exec'),
         dict(__name__='__main__',__file__=str(BASE/'analyze-bluetooth-431.generated.py')))

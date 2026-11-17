"""Analyze532 independently of earlier failed candidates."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
if __name__ == '__main__':
    source=(BASE/'analyze-share-kernel-509.py').read_text()
    source=source.replace('commercial61-native-502','commercial61-native-532')
    source=source.replace('share-kernel-analysis-509.json','share-analysis-538.json')
    exec(compile(source,str(BASE/'analyze-share-532-538.generated.py'),'exec'),
         dict(__name__='__main__',__file__=str(BASE/'analyze-share-532-538.generated.py')))
